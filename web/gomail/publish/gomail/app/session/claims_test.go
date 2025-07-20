package session

import (
	"testing"
	"time"
)

func TestSerialize(t *testing.T) {
	email := "test@test.com"
	isAdmin := false
	sc := SessionClaims{
		Email:   email,
		Expiry:  time.Now().Unix() + 86400,
		IsAdmin: isAdmin,
	}
	ss := NewSessionSerializer()
	_, err := ss.Serialize(&sc)
	if err != nil {
		t.Fatal(err)
	}
}

func TestDeserialize(t *testing.T) {
	email := "admin@test.com"
	isAdmin := true
	sc := SessionClaims{
		Email:   email,
		Expiry:  time.Now().Unix() + 86400,
		IsAdmin: isAdmin,
	}

	ss := NewSessionSerializer()
	s, err := ss.Serialize(&sc)
	if err != nil {
		t.Fatal(err)
	}

	dsc := SessionClaims{}
	err = ss.Deserialize(s, &dsc)
	if err != nil {
		t.Fatal(err)
	}

	if dsc.Email != sc.Email {
		t.Fatalf("expected email to be %s, but got %s", sc.Email, dsc.Email)
	}

	if dsc.Expiry != sc.Expiry {
		t.Fatalf("expected email to be %d, but got %d", sc.Expiry, dsc.Expiry)
	}

	if dsc.IsAdmin != sc.IsAdmin {
		t.Fatalf("expected isAdmin to be %t, but got %t", sc.IsAdmin, dsc.IsAdmin)
	}
}
