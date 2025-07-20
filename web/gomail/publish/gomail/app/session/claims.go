package session

import (
	"bytes"
	"encoding/binary"
	"io"
)

const (
	boolTrue  = "t"
	boolFalse = "f"
)

type SessionClaims struct {
	Email   string
	Expiry  int64
	IsAdmin bool
}

type SessionSerializer struct {
	buf *bytes.Buffer
}

func NewSessionSerializer() *SessionSerializer {
	return &SessionSerializer{
		buf: new(bytes.Buffer),
	}
}

func (ss *SessionSerializer) growBuf(n int) {
	a := ss.buf.Available()
	if a < n {
		ss.buf.Grow(n - a)
	}
}

func (ss *SessionSerializer) writeLength(l int) {
	el := uint16(l)
	ss.growBuf(2)
	bs := make([]byte, 2)
	binary.LittleEndian.PutUint16(bs, el)
	ss.buf.Write(bs)
}

func (ss *SessionSerializer) writeEmail(email string) {
	ss.writeLength(len(email))
	ss.buf.WriteString(email)
}

func (ss *SessionSerializer) writeExpiry(expiry int64) {
	ss.growBuf(8)
	bs := make([]byte, 8)
	binary.LittleEndian.PutUint64(bs, uint64(expiry))
	ss.buf.Write(bs)
}

func (ss *SessionSerializer) writeIsAdmin(isAdmin bool) {
	ss.growBuf(1)
	if isAdmin {
		ss.buf.WriteString(boolTrue)
	} else {
		ss.buf.WriteString(boolFalse)
	}
}

func (ss *SessionSerializer) Serialize(s *SessionClaims) ([]byte, error) {
	ss.writeEmail(s.Email)
	ss.writeExpiry(s.Expiry)
	ss.writeIsAdmin(s.IsAdmin)
	return io.ReadAll(ss.buf)
}

func (ss *SessionSerializer) readBytes(n int) (bts []byte, err error) {
	b := make([]byte, n)
	_, err = ss.buf.Read(b)
	if err != nil {
		return nil, err
	}
	return b, nil
}

func (ss *SessionSerializer) readLength() (len int, err error) {
	lb, err := ss.readBytes(2)
	if err != nil {
		return -1, err
	}
	l16 := binary.LittleEndian.Uint16(lb)
	return int(l16), nil
}

func (ss *SessionSerializer) readEmail() (email string, err error) {
	l, err := ss.readLength()
	if err != nil {
		return "", err
	}
	eb, err := ss.readBytes(l)
	if err != nil {
		return "", err
	}
	return string(eb), err
}

func (ss *SessionSerializer) readExpiry() (expiry int64, err error) {
	bexp, err := ss.readBytes(8)
	if err != nil {
		return -1, err
	}
	eui := binary.LittleEndian.Uint64(bexp)
	return int64(eui), nil
}

func (ss *SessionSerializer) readIsAdmin() (isAdmin bool, err error) {
	iab, err := ss.readBytes(1)
	if err != nil {
		return false, err
	}
	return string(iab) == boolTrue, nil
}

func (ss *SessionSerializer) Deserialize(sd []byte, sc *SessionClaims) (err error) {
	ss.buf = bytes.NewBuffer(sd)
	email, err := ss.readEmail()
	if err != nil {
		return err
	}
	sc.Email = email
	expiry, err := ss.readExpiry()
	if err != nil {
		return err
	}
	sc.Expiry = expiry

	isAdmin, err := ss.readIsAdmin()
	if err != nil {
		return err
	}
	sc.IsAdmin = isAdmin

	return nil
}
