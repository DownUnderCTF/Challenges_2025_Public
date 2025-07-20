package main

import (
	"bufio"
	"crypto/rand"
	"crypto/rsa"
	"crypto/tls"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/pem"
	"fmt"
	"log"
	"math/big"
	"net"
	"net/url"
	"os"
	"strings"
	"time"
)

const (
	CALL = "Moonlight reflects twice on still water\n"
	RESP = "But+ripples+show=truth%in motion"
	// RESP      = "Password"
	PORT      = "30063"
	CERT_FILE = "./cert.pem"
	KEY_FILE  = "./key.pem"
)

func main() {
	var listener net.Listener
	var tlsConfig *tls.Config
	var err error

	if len(os.Args) > 1 {
		cert, err := tls.LoadX509KeyPair(CERT_FILE, KEY_FILE)
		if err != nil {
			log.Printf("Could not load certificate/key pair: %v. Generating new ones.", err)
			if err := generateCertificate(); err != nil {
				log.Fatalf("Failed to generate certificate: %v", err)
			}
			cert, err = tls.LoadX509KeyPair(CERT_FILE, KEY_FILE)
			if err != nil {
				log.Fatalf("Failed to load certificate/key pair after generation: %v", err)
			}
		}
		tlsConfig = &tls.Config{
			Certificates: []tls.Certificate{cert},
		}
		listener, err = tls.Listen("tcp", ":"+PORT, tlsConfig)
		if err != nil {
			log.Fatalf("Failed to listen on port %s: %v", PORT, err)
		}
	} else {
		listener, err = net.Listen("tcp", ":"+PORT)
		if err != nil {
			log.Fatalf("Failed to listen on port %s: %v", PORT, err)
		}
	}
	defer listener.Close()
	log.Printf("Gemini server listening securely on port %s", PORT)

	for {
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Failed to accept connection: %v", err)
			continue
		}
		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()
	conn.SetReadDeadline(time.Now().Add(10 * time.Second))

	request_url, err := bufio.NewReader(conn).ReadString('\n')
	if err != nil {
		log.Printf("Failed to read from connection: %v", err)
		return
	}
	request_url = strings.TrimSpace(request_url)

	u, err := url.Parse(request_url)
	if err != nil {
		log.Printf("Could not parse URL %q: %v", request_url, err)
		fmt.Fprintf(conn, "59 BAD REQUEST\r\n")
		return
	}

	log.Printf("Received request for: %s", u.Path)

	switch u.Path {
	case "/":
		response_body := "# Admin Panel\n\nThis page is under construction!\n\nIf you are the admin, you should login\n=> password_protected.gmi Login\n"
		fmt.Fprintf(conn, "20 text/gemini\r\n%s", response_body)

	case "/password_protected.gmi":
		submitted_query := u.RawQuery

		if submitted_query == "" {
			fmt.Fprintf(conn, "11 %s:\r\n", CALL)
		} else {
			decoded_response, err := url.QueryUnescape(submitted_query)
			log.Print("Password Attempt: ", decoded_response)
			if err != nil {
				log.Printf("Failed to unescape query: %v", err)
				fmt.Fprintf(conn, "59 BAD REQUEST\r\n")
				return
			}

			if decoded_response == RESP {
				response_body := "# Welcome, Admin!\n\nYou have successfully logged in.\n> DUCTF{Cr1pPl3_Th3_1nFr4sTrUCtu53}"
				fmt.Fprintf(conn, "20 text/gemini\r\n%s", response_body)
			} else {
				fmt.Fprintf(conn, "60 Incorrect Password\r\n")
			}
		}

	default:
		fmt.Fprintf(conn, "51 NOT FOUND\r\n")
	}
}

func generateCertificate() error {
	log.Println("Generating new self-signed certificate...")

	priv_key, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return fmt.Errorf("failed to generate private key: %w", err)
	}

	template := x509.Certificate{
		SerialNumber: big.NewInt(1),
		Subject: pkix.Name{
			Organization: []string{"My Gemini Server"},
		},
		NotBefore: time.Now(),
		NotAfter:  time.Now().AddDate(10, 0, 0), // Valid for 10 years.

		KeyUsage:              x509.KeyUsageKeyEncipherment | x509.KeyUsageDigitalSignature,
		ExtKeyUsage:           []x509.ExtKeyUsage{x509.ExtKeyUsageServerAuth},
		BasicConstraintsValid: true,
		DNSNames:              []string{"localhost"},
	}

	der_bytes, err := x509.CreateCertificate(rand.Reader, &template, &template, &priv_key.PublicKey, priv_key)
	if err != nil {
		return fmt.Errorf("failed to create certificate: %w", err)
	}

	cert_out, err := os.Create(CERT_FILE)
	if err != nil {
		return fmt.Errorf("failed to open cert.pem for writing: %w", err)
	}
	pem.Encode(cert_out, &pem.Block{Type: "CERTIFICATE", Bytes: der_bytes})
	cert_out.Close()
	log.Printf("Saved certificate to %s", CERT_FILE)

	key_out, err := os.OpenFile(KEY_FILE, os.O_WRONLY|os.O_CREATE|os.O_TRUNC, 0600)
	if err != nil {
		return fmt.Errorf("failed to open key.pem for writing: %w", err)
	}
	pem.Encode(key_out, &pem.Block{Type: "RSA PRIVATE KEY", Bytes: x509.MarshalPKCS1PrivateKey(priv_key)})
	key_out.Close()
	log.Printf("Saved private key to %s", KEY_FILE)

	return nil
}
