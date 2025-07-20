#include <ctype.h>
#include <stdarg.h>
#include <stdlib.h>
#include <sys/random.h>
/* clang-format off */
#include <stdio.h>              /* stdio.h needs to come before gmp.h */
#include <gmp.h>
/* clang-format on */

#define STATUS_SUCCESS 0
#define STATUS_FAIL 1

#define PRIVKEY_SIZE 2184
#define HEXSTRING_SIZE 1024

static char *hexstring = NULL;

void print_flag() {
  char *flag;
  flag = getenv("FLAG");
  puts(flag ? flag : "DUCTF{test_flag}");
}

void submit_answer(mpz_t pub, mpz_t g, mpz_t p, mpz_t guess) {
  puts("Enter your guess (hex): ");
  mpz_inp_str(guess, stdin, 16);

  mpz_powm_sec(guess, g, guess, p);
  if (mpz_cmp(guess, pub) == 0) {
    print_flag();
  } else {
    puts("Incorrect!");
  }
}

void menu() {
  puts("1> Print public key");
  puts("2> Start over");
  puts("3> Submit answer");
  puts("4> Exit");
  puts("> ");
}

void print_public_key(mpz_t pub, mpz_t priv, mpz_t g, mpz_t p) {
  mpz_powm_sec(pub, g, priv, p);

  hexstring = mpz_get_str(hexstring, 16, pub);
  printf("Public Key: %s\n", hexstring);
}

int init(mpz_t pub, mpz_t priv, mpz_t g, mpz_t q, mpz_t p) {
  int ret;
  mp_limb_t *buf;
  size_t nb = PRIVKEY_SIZE;

  /* mod */
  mpz_set_str(
      p,
      "C2F2E0F7EC137C1F4F67D5B4276756FCDA5D5DAADDE9993AD2289D7CA855F50BCEC64FE5"
      "859C503A654F32422C5C02B5083BC83DB66EECBD347B971C0ACEF5A387C5E90FCFD25F87"
      "F565752574CC4D72E1AFE0E09A1FBFDE1F1960A56226523BD67B0E7FDE83FE53F85AC61D"
      "94AB52D837CCC1120F22D58CA79334E23B66AD23B1CB493F5DC8E2B7",
      16);

  /* order */
  mpz_sub_ui(q, p, 1);
  mpz_divexact_ui(q, q, 2);

  /* generator */
  mpz_set_str(g, "2", 10);

  /* private key */
  buf = (mp_limb_t *)malloc(nb);
  if (buf == NULL) {
    puts("init: err malloc");
    ret = STATUS_FAIL;
    goto err;
  }

  size_t nwritten = getrandom(buf, nb, 0);
  if (nwritten < nb) {
    puts("init: err getrandom");
    ret = STATUS_FAIL;
    goto err;
  }

  mpz_roinit_n(priv, buf, nb / sizeof(mp_limb_t));

  /* hexstring */
  if (hexstring == NULL && (hexstring = malloc(HEXSTRING_SIZE)) == NULL) {
    puts("init: err malloc");
    ret = STATUS_FAIL;
    goto err;
  };
  ret = STATUS_SUCCESS;

err:
  free(buf);
  return ret;
}

int main() {
  int ret;
  char c;
  char *outbuffer = NULL;

  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  setvbuf(stdin, NULL, _IONBF, 0);

  mpz_t p, q, g, priv, pub, guess;
  mpz_inits(p, q, g, priv, pub, guess, NULL);

  if (init(pub, priv, g, q, p) == STATUS_FAIL) {
    ret = STATUS_FAIL;
    goto cleanup;
  }
  print_public_key(pub, priv, g, p);

  for (;;) {
    menu();

    do {
      c = getchar();
      if (c == EOF) {
        ret = STATUS_SUCCESS;
        goto cleanup;
      }
    } while (isspace(c));

    switch (c) {
    case '1':
      print_public_key(pub, priv, g, p);
      break;
    case '2':
      if (init(pub, priv, g, q, p) == STATUS_FAIL) {
        ret = STATUS_FAIL;
        goto cleanup;
      }
      break;
    case '3':
      submit_answer(pub, g, p, guess);
      break;
    case '4':
      ret = STATUS_SUCCESS;
      goto cleanup;
    default:
      puts("Invalid choice");
      break;
    }
  }

cleanup:
  puts("Bye!");
  mpz_clears(p, q, g, priv, pub, guess, NULL);
  free(hexstring);
  return ret;
}
