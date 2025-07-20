package main

import (
	"crypto/rand"
	"fat-monke/gomail/session"
	"net/http"

	"github.com/gin-gonic/gin"
)

var SessionKey = make([]byte, 64)
var _, _ = rand.Read(SessionKey)

var MaxBytes int64 = 1024 * 1024 * 1

func MaxBodyMiddleware(maxSize int64) gin.HandlerFunc {
	return func(c *gin.Context) {
		var w http.ResponseWriter = c.Writer
		c.Request.Body = http.MaxBytesReader(w, c.Request.Body, maxSize)

		c.Next()
	}
}

func AttachSessionMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Set("sessionHandler", session.Session{
			Key: SessionKey,
		})

		c.Next()
	}
}

func SessionMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		sH, exists := c.Get("sessionHandler")
		if !exists {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "could not get session handler",
			})
			return
		}

		t := c.Request.Header["X-Auth-Token"]
		if t == nil {
			c.JSON(http.StatusInternalServerError, gin.H{
				"error": "missing \"X-Auth-Token\" header",
			})
			return
		}
		token := t[0]
		var sc session.SessionClaims
		err := sH.(session.Session).Decode(token, &sc)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{
				"error": err,
			})
			return
		}
		c.Set("sessionclaims", sc)
		c.Next()
	}
}
