package session

import (
	"testing"
)

func TestEncode(t *testing.T) {
	s := Session{Key: []byte("test key")}
	e := "test@test.com"
	_, err := s.Encode(e, false)
	if err != nil {
		t.Fatal(err)
	}
}

func TestDecode(t *testing.T) {
	s := Session{Key: []byte("test key")}
	e := "admin@test.com"
	ia := true
	token, err := s.Encode(e, ia)
	if err != nil {
		t.Fatal(err)
	}

	sc := SessionClaims{}
	err = s.Decode(token, &sc)
	if err != nil {
		t.Fatal(err)
	}

	if sc.Email != e {
		t.Fatalf("expected email to be %s, but got %s", e, sc.Email)
	}

	if sc.IsAdmin != ia {
		t.Fatalf("expected isAdmin to be %t, but got %t", ia, sc.IsAdmin)
	}

	it := "A" + token[1:]
	isc := SessionClaims{}
	err = s.Decode(it, &isc)
	if err == nil {
		t.Fatal("should have raised InvalidTokenError")
	}
}
