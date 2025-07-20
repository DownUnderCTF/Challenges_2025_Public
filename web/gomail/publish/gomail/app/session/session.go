package session

import (
	"bytes"
	"compress/gzip"
	"crypto/hmac"
	"crypto/sha256"
	"encoding/base64"
	"io"
	"strings"
	"time"
)

type InvalidTokenError struct{}

func (m *InvalidTokenError) Error() string {
	return "invalid token"
}

type ExpiredTokenError struct{}

func (m *ExpiredTokenError) Error() string {
	return "expired token"
}

type Session struct {
	Key []byte
}

func (se Session) sign(d []byte) []byte {
	mac := hmac.New(sha256.New, se.Key)
	mac.Write(d)
	return mac.Sum(nil)
}

func (se Session) Encode(email string, isAdmin bool) (token string, err error) {
	sc := SessionClaims{
		Email:   email,
		Expiry:  time.Now().Unix() + 86400,
		IsAdmin: isAdmin,
	}
	sr := NewSessionSerializer()
	bts, err := sr.Serialize(&sc)

	if err != nil {
		return "", err
	}

	var buf bytes.Buffer
	w := gzip.NewWriter(&buf)
	_, err = w.Write(bts)
	w.Close()
	if err != nil {
		return "", err
	}

	bts = buf.Bytes()
	sig := se.sign([]byte(bts))

	token = base64.URLEncoding.EncodeToString(bts) + "." + base64.URLEncoding.EncodeToString(sig)

	return token, nil
}

func (se Session) Decode(token string, dstSC *SessionClaims) (err error) {
	ps := strings.SplitN(token, ".", 2)
	if len(ps) != 2 {
		return &InvalidTokenError{}
	}
	bts, err := base64.URLEncoding.DecodeString(ps[0])
	if err != nil {
		return err
	}
	sig, err := base64.URLEncoding.DecodeString(ps[1])
	if err != nil {
		return err
	}
	expSig := se.sign(bts)
	if !hmac.Equal(sig, expSig) {
		return &InvalidTokenError{}
	}
	buf := bytes.NewReader(bts)
	r, err := gzip.NewReader(buf)
	if err != nil {
		return err
	}
	bts, err = io.ReadAll(r)
	r.Close()
	if err != nil {
		return err
	}
	sr := NewSessionSerializer()
	err = sr.Deserialize(bts, dstSC)
	if err != nil {
		return err
	}
	if time.Now().Unix() > dstSC.Expiry {
		return &ExpiredTokenError{}
	}
	return nil
}
