gomail
============

The application is a simple `golang` web application, where the flag is saved as an email for the "mc-fat@monke.zip" email.

The application has two endpoints:

```
app-1  | [GIN-debug] POST   /login                    --> main.LoginHandler (5 handlers)
app-1  | [GIN-debug] GET    /emails                   --> main.GetEmailsHandler (6 handlers)
```

Looking at the `POST /login` endpoint, it shows that if "mc-fat@monke.zip" is provided as the `email` in the JSON request then it validates the password and otherwise it creates a guest session.

*`app/handlers.go`*
```go
...

var fatMonkeEmail = "mc-fat@monke.zip"
var guestEmail = "guest"

var fatMonkePass = make([]byte, 64)
var _, _ = rand.Read(fatMonkePass)

var userLogins = map[string][]byte{
	fatMonkeEmail: fatMonkePass, <1>
}

...

type loginReq struct {
	Email    string `json:"email" binding:"required,email"`
	Password string `json:"password" binding:"required"`
}

func LoginHandler(c *gin.Context) {
	var lr loginReq
	var err error

	if err = c.BindJSON(&lr); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": "error reading json",
		})
		return
	}

	isAdmin := false
	usrPass := userLogins[lr.Email] <1>
	if usrPass != nil {
		if subtle.ConstantTimeCompare([]byte(lr.Password), usrPass) == 1 {
			isAdmin = true
		} else {
			lr.Email = guestEmail
		}
	}
	sH, exists := c.Get("sessionHandler")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "could not get session handler",
		})
		return
	}

	token, err := sH.(session.Session).Encode(lr.Email, isAdmin) <2>

	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{
			"error": err,
		})
		return
	}
	c.JSON(http.StatusOK, gin.H{
		"token": token,
	})
}
```
<1> Trying to login as "mc-fat@monke.zip" performs a password validation check, where if it fails it sets the email to "guest" and `IsAdmin = false`.

<2> If an email is provided besides "mc-fat@monke.zip", then a guest session token is created using the user provided `email`.

Digging into how the session claims are serialised in the authentication token, there is an integer overflow bug with the writing of the `email` input.

*`app/session/claims.go`*
```go
func (ss *SessionSerializer) writeLength(l int) {
	el := uint16(l) <1>
	ss.growBuf(2)
	bs := make([]byte, 2)
	binary.LittleEndian.PutUint16(bs, el)
	ss.buf.Write(bs)
}

func (ss *SessionSerializer) writeEmail(email string) {
	ss.writeLength(len(email))
	ss.buf.WriteString(email) <2>
}

...

func (ss *SessionSerializer) Serialize(s *SessionClaims) ([]byte, error) {
	ss.writeEmail(s.Email)
	ss.writeExpiry(s.Expiry)
	ss.writeIsAdmin(s.IsAdmin)
	return io.ReadAll(ss.buf)
}
```
<1> Casts the `int` (signed integer at least 32 bits) to `uint16`, which silently overflows if the length of the email is over 65535 bytes long.

<2> [`Buffer.WriteString`](https://pkg.go.dev/bytes#Buffer.WriteString) writes `len(email)`, which would be larger than the length prefix that was cast using `uint16` if the email is over 65535 bytes long.

The integer overflow can be exploited to truncate the `email` section in the authentication token so when the authentication token is decoded it reads "mc-fat@monke.zip" as the email for the user. The following `python` snippet demonstrates a payload for the `email` input that exploits this integer overflow:

*example poc for the `email` input for the `POST /login` endpoint*
```python
"mc-fat@monke.zip" + "z"*8 +"t" + "A"*((1 << 16) - 9)
```

Exampling the POC further:
- `"z"*8` is "zzzzzzzz" which is needed to overwrite the expiry section in the authentication token. When the token is deserialised it will be decoded as the `8825501086245354106` (a `int32` number).
- `t` is for changing the `IsAdmin` section in the token from `f` (for `false`) to `true`.
- `"A"*((1 << 16) - 9)` fills in bytes so the email has a length greater than 65535 bytes. The `- 9` is so that the length for the email section would write be 16 (the length of "mc-fat@monke.zip").

[`solve.py`](./solve.py) contains the full POC.