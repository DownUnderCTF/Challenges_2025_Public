package main

import (
	"fmt"
	"io"
	"log"
	"net/url"
	"strings"
	"sync"

	"github.com/makeworld-the-better-one/go-gemini"
)

const searchString = "DUCTF"

const startingURL = "gemini://localhost:1965"

var (
	found      = make(map[string]bool)
	foundMutex = &sync.Mutex{}
)

var (
	visited      = make(map[string]bool)
	visitedMutex = &sync.Mutex{}
)

var wg sync.WaitGroup

func main() {
	client := &gemini.Client{}
	fmt.Printf("Starting crawl at %s\n", startingURL)
	wg.Add(1)
	go crawl(client, startingURL)
	wg.Wait()

	fmt.Println("\n--- Search Complete ---")
	if len(found) > 0 {
		fmt.Printf("Found '%s' on the following pages:\n", searchString)
		for u := range found {
			fmt.Println(u)
		}
	} else {
		fmt.Printf("Could not find '%s' on any page.\n", searchString)
	}
}

// crawl recursively crawls a Gemini URL.
func crawl(client *gemini.Client, rawURL string) {
	defer wg.Done()

	// Parse and normalize the URL.
	u, err := url.Parse(rawURL)
	if err != nil {
		fmt.Printf("Invalid URL: %s\n", rawURL)
		return
	}

	visitedMutex.Lock()
	if visited[u.String()] {
		visitedMutex.Unlock()
		return
	}
	visited[u.String()] = true
	visitedMutex.Unlock()

	fmt.Printf("Crawling: %s\n", u.String())

	resp, err := client.Fetch(u.String())
	if err != nil {
		return
	}
	defer func() {
		_ = resp.Body.Close()
	}()

	if resp.Status != 20 {
		log.Printf("%+v", resp)
		log.Printf("Non-success status for %s: %v", u.String(), resp.Status)
		return
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		log.Printf("Failed to read body of %s: %v", u.String(), err)
		return
	}

	if strings.Contains(string(body), searchString) {
		foundMutex.Lock()
		found[u.String()] = true
		foundMutex.Unlock()
	}

	if strings.HasPrefix(resp.Meta, "text/gemini") {
		lines := strings.SplitSeq(string(body), "\n")
		for line := range lines {
			if strings.HasPrefix(line, "=>") {
				parts := strings.Fields(line)
				if len(parts) > 1 {
					linkURL := parts[1]
					absoluteURL, err := u.Parse(linkURL)
					if err == nil {
						wg.Add(1)
						go crawl(client, absoluteURL.String())
					}
				}
			}
		}
	}
}
