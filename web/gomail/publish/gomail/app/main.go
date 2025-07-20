package main

import (
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()
	r.Use(MaxBodyMiddleware(MaxBytes))
	r.Use(AttachSessionMiddleware())

	r.POST("/login", LoginHandler)
	r.GET("/emails", SessionMiddleware(), GetEmailsHandler)

	r.Run("0.0.0.0:1337")
}
