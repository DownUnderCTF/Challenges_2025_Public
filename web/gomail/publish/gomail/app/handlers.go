package main

import (
	"crypto/rand"
	"crypto/subtle"
	"fat-monke/gomail/session"
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
)

var fatMonkeEmail = "mc-fat@monke.zip"
var guestEmail = "guest"

var fatMonkePass = make([]byte, 64)
var _, _ = rand.Read(fatMonkePass)

var userLogins = map[string][]byte{
	fatMonkeEmail: fatMonkePass,
}

type email struct {
	From    string `json:"from"`
	To      string `json:"to"`
	Subject string `json:"subject"`
	Data    string `json:"data"`
}

var emails = map[string][]email{
	fatMonkeEmail: {
		email{
			From:    "admin@duc.tf",
			To:      fatMonkeEmail,
			Subject: "Your New Challenge Flag",
			Data: fmt.Sprintf(`Hey MC Fat Monke,

We heard once again you accidentally leaked your flag for your last challenge...

Bruh stop doing that...

Here is your new flag for your challenge, please stop leaking it...

Flag: %s

From DUCTF Admin
`, GetEnvWithDefault("FLAG", "FAKE{get_the_flag_from_the_instance}")),
		},
	},
	guestEmail: {
		email{
			From:    "mc-fat@monke.zip",
			To:      guestEmail,
			Subject: "Noice Try Hacker",
			Data: `Hey hacker,

Told ya you can't hack into my private email server. I have this locked down ya donke.
		`,
		}},
}

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
	usrPass := userLogins[lr.Email]
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

	token, err := sH.(session.Session).Encode(lr.Email, isAdmin)

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

func GetEmailsHandler(c *gin.Context) {
	scr, exists := c.Get("sessionclaims")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "could not get session handler",
		})
		return
	}

	sc := scr.(session.SessionClaims)

	email := sc.Email
	iA := sc.IsAdmin
	if !iA {
		email = guestEmail
	}
	c.JSON(http.StatusOK, gin.H{
		"emails": emails[email],
	})
}
