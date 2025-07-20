package main

import (
	"context"
	"crypto/subtle"
	"fmt"
	"io"
	"log"
	"net/http"
	"regexp"
	"time"

	"github.com/redis/go-redis/v9"
)

var ctx = context.Background()
var rdb *redis.Client

const (
	rewriteURL    = "http://127.0.0.1:3000$3"
	proxiedHeader = "X-Proxied"
)

func init() {
	rdb = redis.NewClient(&redis.Options{Addr: "127.0.0.1:6379"})
}

func ValidateAuthToken(req *http.Request) (bool, error) {
	u, p, ok := req.BasicAuth()
	if !ok {
		return false, fmt.Errorf("missing auth header")
	}

	res, err := rdb.Get(ctx, u).Result()
	if err != nil {
		return false, err
	}
	return subtle.ConstantTimeCompare([]byte(p), []byte(res)) == 1, nil
}

func proxiedUrl(ou string) (newUrl string) {
	re := regexp.MustCompile(`^(https?://)(.*)(/.*)$`)
	newUrl = re.ReplaceAllString(ou, rewriteURL)
	return newUrl
}

func buildAbsUrl(req *http.Request) (absUrl string, err error) {
	ba := ""
	u, p, ok := req.BasicAuth()
	if ok {
		ba = u + ":" + p + "@"
	}

	return fmt.Sprintf("http://%s%s%s", ba, req.Host, req.URL.RequestURI()), nil
}

func ProxyHandler(w http.ResponseWriter, req *http.Request) {
	if req.Header.Get(proxiedHeader) != "" {
		http.Error(w, "bad gateway", http.StatusBadGateway)
		return
	}
	ar, err := ValidateAuthToken(req)
	if err != nil || !ar {
		http.Error(w, "invalid authentication token", http.StatusUnauthorized)
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
		newReq.Header.Add(k, vs[0])
	}

	newReq.Header.Add(proxiedHeader, "true")
	client := &http.Client{
		CheckRedirect: func(req *http.Request, via []*http.Request) error {
			return http.ErrUseLastResponse
		},
		Timeout: 10 * time.Second,
	}

	res, err := client.Do(newReq)
	if err != nil {
		http.Error(w, "bad gateway", http.StatusBadGateway)
		return
	}

	if res.StatusCode != http.StatusOK {
		http.Error(w, "backend rejected your request", http.StatusBadRequest)
		return
	}

	defer res.Body.Close()
	b, err := io.ReadAll((res.Body))
	if err != nil {
		http.Error(w, "bad gateway", http.StatusBadGateway)
		return
	}

	w.WriteHeader(res.StatusCode)
	for k, vs := range res.Header {
		w.Header().Set(k, vs[0])
	}
	w.Write(b)
}

func main() {
	http.HandleFunc("/", ProxyHandler)
	log.Fatal(http.ListenAndServe(":1337", nil))
}
