package main

import (
	"net/http"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
)

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
