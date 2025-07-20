#include "cosigner/cmp_ecdsa_online_signing_service.h"
#include "cosigner/cmp_setup_service.h"
#include "crypto/GFp_curve_algebra/GFp_curve_algebra.h"
#include "include/platform.hpp"
#include "include/serialization.hpp"
#include "include/setup.hpp"
#include "include/signing.hpp"
#include <boost/json.hpp>
#include <ext/stdio_filebuf.h>
#include <fcntl.h>
#include <iostream>
#include <stdio.h>
#include <string>
#include <unistd.h>
#include <uuid/uuid.h>

#define SERVER_ID 0
#define CLIENT_ID 1

using namespace fireblocks::common::cosigner;
using filebuf_t = __gnu_cxx::stdio_filebuf<char>;
using namespace boost::json;

const char *keyid = "downunderctf";

std::ostream &out() {
  static std::ostream *p = []() -> std::ostream * {
    int fd = dup(STDOUT_FILENO);
    FILE *fp = fdopen(fd, "w");
    static __gnu_cxx::stdio_filebuf<char> buf(fp, std::ios::out);
    static std::ostream os(&buf);

    int nullfd = open("/dev/null", O_WRONLY);
    dup2(nullfd, STDOUT_FILENO);
    close(nullfd);

    return &os;
  }();
  return *p;
}

void ecdsa_sign(players_setup_info &players, cosigner_sign_algorithm type,
                const std::string &keyid, uint32_t count,
                const elliptic_curve256_point_t &pubkey,
                const byte_vector_t &chaincode,
                const std::vector<std::vector<uint32_t>> &paths, uint64_t my_id,
                BIGNUM *p) {
  uuid_t uid;
  char txid[37] = {0};

  if (my_id == SERVER_ID) {
    uuid_generate_random(uid);
    uuid_unparse(uid, txid);

    object jo;
    jo.emplace("tx_id", txid);
    out() << jo << std::endl;
  } else {
    value jv = read_json_object();
    string js = jv.as_object().at("tx_id").as_string();
    std::copy_n(js.begin(), std::min(js.size(), sizeof(txid)), txid);
  }

  std::map<uint64_t, std::unique_ptr<signing_info>> services;
  std::set<uint64_t> players_ids;
  std::set<std::string> players_str;

  for (auto i = players.begin(); i != players.end(); ++i) {
    auto info = std::make_unique<signing_info>(i->first, i->second);
    services.emplace(i->first, std::move(info));
    players_ids.insert(i->first);
    players_str.insert(std::to_string(i->first));
  }

  assert(chaincode.size() == sizeof(HDChaincode));

  signing_data data;
  memcpy(data.chaincode, chaincode.data(), sizeof(HDChaincode));
  for (size_t i = 0; i < count; i++) {
    signing_block_data block;
    block.data.insert(block.data.begin(), 32, '0');
    block.path = paths[i];
    data.blocks.push_back(block);
  }

  std::map<uint64_t, std::vector<cmp_mta_request>> mta_requests;
  {
    auto &request = mta_requests[my_id];
    services[my_id]->signing_service.start_signing(
        keyid, txid, type, data, "", players_str, players_ids, request, p);
    object jo;
    jo["mta_requests"] = value_from(request);
    out() << jo << std::endl;

    value jv = read_json_object();
    mta_requests[!my_id] = value_to<std::vector<cmp_mta_request>>(
        jv.as_object().at("mta_requests"));
  }

  std::map<uint64_t, cmp_mta_responses> mta_responses;
  {
    auto &response = mta_responses[my_id];
    services[my_id]->signing_service.mta_response(
        txid, mta_requests, MPC_CMP_ONLINE_VERSION, response);
    object jo;
    jo["mta_response"] = value_from(response);
    out() << jo << std::endl;

    value jv = read_json_object();
    mta_responses[!my_id] =
        value_to<cmp_mta_responses>(jv.as_object().at("mta_response"));
  }
  mta_requests.clear();

  std::map<uint64_t, std::vector<cmp_mta_deltas>> deltas;
  {
    auto &delta = deltas[my_id];
    services[my_id]->signing_service.mta_verify(txid, mta_responses, delta, p);
    out() << "abort" << std::endl;
    return;
  }
}

void create_secret(players_setup_info &players, cosigner_sign_algorithm type,
                   const std::string &keyid, elliptic_curve256_point_t &pubkey,
                   uint64_t my_id) {
  std::unique_ptr<elliptic_curve256_algebra_ctx_t,
                  void (*)(elliptic_curve256_algebra_ctx_t *)>
      algebra(elliptic_curve256_new_secp256k1_algebra(),
              elliptic_curve256_algebra_ctx_free);

  const size_t PUBKEY_SIZE = algebra->point_size(algebra.get());
  memset(pubkey, 0, sizeof(elliptic_curve256_point_t));

  std::cerr << "keyid = " << keyid << std::endl;
  std::vector<uint64_t> players_ids;
  std::map<uint64_t, std::unique_ptr<setup_info>> services;

  for (auto i = players.begin(); i != players.end(); ++i) {
    services.emplace(i->first,
                     std::make_unique<setup_info>(i->first, i->second));
    players_ids.push_back(i->first);
  }

  std::map<uint64_t, commitment> commitments;
  {
    commitment &commit = commitments[my_id];
    services[my_id]->setup_service.generate_setup_commitments(
        keyid, TENANT_ID, type, players_ids, players_ids.size(), 0, {}, commit);
    object jo;
    jo["commitment"] = value_from(commit);
    out() << jo << std::endl;

    value jv = read_json_object();
    commitments[!my_id] = value_to<commitment>(jv.as_object().at("commitment"));
  }

  std::map<uint64_t, setup_decommitment> decommitments;
  {

    setup_decommitment &decommitment = decommitments[my_id];
    services[my_id]->setup_service.store_setup_commitments(keyid, commitments,
                                                           decommitment);
    object jo;
    jo["decommitment"] = value_from(decommitment);
    out() << jo << std::endl;

    value jv = read_json_object();
    decommitments[!my_id] =
        value_to<setup_decommitment>(jv.as_object().at("decommitment"));
  }
  commitments.clear();

  std::map<uint64_t, setup_zk_proofs> proofs;
  {
    setup_zk_proofs &proof = proofs[my_id];
    services[my_id]->setup_service.generate_setup_proofs(keyid, decommitments,
                                                         proof);

    object jo;
    jo["setup_zk_proof"] = value_from(proof);
    out() << jo << std::endl;

    value jv = read_json_object();
    proofs[!my_id] =
        value_to<setup_zk_proofs>(jv.as_object().at("setup_zk_proof"));
  }
  decommitments.clear();

  std::map<uint64_t, std::map<uint64_t, byte_vector_t>>
      paillier_large_factor_proofs;
  {
    auto &proof = paillier_large_factor_proofs[my_id];
    services[my_id]->setup_service.verify_setup_proofs(keyid, proofs, proof);
    object jo;
    jo["paillier_large_factor_proof"] = value_from(proof);
    out() << jo << std::endl;

    value jv = read_json_object();
    paillier_large_factor_proofs[!my_id] =
        value_to<std::map<uint64_t, byte_vector_t>>(
            jv.as_object().at("paillier_large_factor_proof"));
  }
  proofs.clear();

  {
    std::string public_key;
    cosigner_sign_algorithm algorithm;
    services[my_id]->setup_service.create_secret(
        keyid, paillier_large_factor_proofs, public_key, algorithm);
    assert(algorithm == type);
    assert(public_key.size() == PUBKEY_SIZE);
    memcpy(pubkey, public_key.data(), PUBKEY_SIZE);

    object jo;
    jo["public_key"] =
        value_from(std::vector<uint8_t>(public_key.begin(), public_key.end()));
    std::cerr << jo << std::endl;
  }

  paillier_large_factor_proofs.clear();
}

BIGNUM *crt(const std::vector<BIGNUM *> &r, const std::vector<BIGNUM *> &m,
            BN_CTX *ctx) {

  if (r.size() != m.size() || r.empty())
    return nullptr;

  BIGNUM *M = BN_new();
  BIGNUM *sum = BN_new();
  if (!sum) {
    return nullptr;
  }

  BN_one(M);
  for (auto mod : m)
    BN_mul(M, M, mod, ctx);

  BN_zero(sum);

  for (size_t i = 0; i < m.size(); ++i) {
    BIGNUM *Mi = BN_new();
    BIGNUM *inv = BN_new();
    BIGNUM *term = BN_new();

    BN_div(Mi, nullptr, M, m[i], ctx);
    if (!BN_mod_inverse(inv, Mi, m[i], ctx)) {
      return nullptr;
    }
    BN_mod_mul(term, r[i], Mi, M, ctx);
    BN_mod_mul(term, term, inv, M, ctx);
    BN_mod_add(sum, sum, term, M, ctx);
  }

  BIGNUM *result = BN_new();
  BN_mod(result, sum, M, ctx);
  return result;
}

int main(int argc, char **argv) {
  out();

  uint64_t my_id;
  if (argc > 1 && argv[1][0] == 'c') {
    my_id = CLIENT_ID;
  } else {
    my_id = SERVER_ID;
  }

  byte_vector_t chaincode(32, '\0');
  std::vector<uint32_t> path = {44, 0, 0, 0, 0};
  elliptic_curve256_point_t pubkey;
  players_setup_info players;

  players[SERVER_ID];
  players[CLIENT_ID];

  create_secret(players, ECDSA_SECP256K1, keyid, pubkey, my_id);

  auto p = BN_new();

  std::vector<int> primes = {
      32783, 32941, 32971, 33107, 33181, 33413, 33563, 33829, 33893, 34261,
      34327, 34351, 34421, 34897, 34913, 36269, 36299, 36389, 36683, 36901,
      37013, 37361, 37397, 37549, 37571, 37633, 37649, 38333, 38351, 38603,
      39019, 39181, 39443, 39719, 39877, 39979, 40129, 40637, 40763, 41047,
      41143, 41941, 42017, 42023, 42571, 42821, 42901, 42979, 43313, 43481,
      43991, 44059, 44111, 44129, 44453, 44483, 44537, 44729, 45137, 45233,
      45293, 45557, 45959, 46523, 46573, 46751, 46831, 46997, 47869, 47963,
      47977, 48049, 48079, 48091, 48299, 48527, 48947, 49057, 49367, 50221,
      50341, 50627, 50773, 50951, 51031, 51517, 52021, 52387, 52711, 52747,
      52757, 52889, 53507, 54851, 55051, 55163, 55763, 55793, 55813, 55949,
      56531, 56807, 56843, 56929, 57143, 57689, 57727, 57787, 58211, 58631,
      58699, 59359, 59417, 59557, 59567, 60013, 60659, 61343, 61409, 61643,
      62497, 62591, 63149, 63199, 63391, 63463, 63587, 64187, 64271, 64667,
      64783, 65101};

  std::vector<BIGNUM *> bn_primes;
  std::vector<BIGNUM *> residues;
  auto ctx = BN_CTX_new();
  auto res = BN_new();
  auto sub = BN_new();
  auto div = BN_new();
  auto n = BN_new();
  BN_dec2bn(&n, "24632200664202953556760214350989832506731078340880868623826325"
                "3223542933217288477"
                "72918094784311476820481094708839148424445242181928634447515485"
                "9397239820000835107"
                "33139127900737294408779803368986290935084498488056492055283402"
                "7425097997412964472"
                "01882465457036798115690095320729247628304919441029280084992670"
                "0833806335846878001"
                "75151929879939151524509443877348342758240122146971375345064874"
                "3757172501797413235"
                "76497788546253631731296579005876314544276985314031354767096506"
                "2220116765654843496"
                "78305717899716112214343218340442164929138797648570589662194728"
                "9442620372166025321"
                "00864782756133558733826531852546936909700741538137");

  for (auto pw : primes) {
    BN_set_word(p, pw);
    try {
      std::cerr << "entering" << std::endl;
      BN_copy(div, p);

      ecdsa_sign(players, ECDSA_SECP256K1, keyid, 1, pubkey, chaincode, {path},
                 my_id, p);
      std::cerr << "challenge.cpp: decrypted alpha = ";
      BN_print_fp(stderr, p);
      std::cerr << std::endl;

      bn_primes.push_back(BN_dup(div));
      BN_div(div, NULL, n, div, ctx);
      BN_mod(sub, p, div, ctx);
      BN_sub(res, p, sub);
      BN_div(res, NULL, res, div, ctx);
      residues.push_back(BN_dup(res));

      std::cerr << "challenge.cpp: private key modulus = ";
      BN_print_fp(stderr, res);
      std::cerr << std::endl;

      std::cerr << "residue size: " << residues.size() << std::endl;
      ;
      std::cerr << "prime size: " << bn_primes.size() << std::endl;
      ;

      if (residues.size() >= 17) {
        break;
      }

    } catch (...) {
      object jo;
      jo = {{"choice", "continue"}};
      out() << jo << std::endl;
    }
  }

  for (auto res : residues) {
    std::cerr << "residue =: ";
    BN_print_fp(stderr, res);
    std::cerr << std::endl;
  }

  for (auto p : bn_primes) {
    std::cerr << "prime =: ";
    BN_print_fp(stderr, p);
    std::cerr << std::endl;
  }

  std::cerr << "residue size: " << residues.size() << std::endl;
  ;
  std::cerr << "prime size: " << bn_primes.size() << std::endl;
  ;
  auto key = crt(residues, bn_primes, ctx);
  if (!key) {
    std::cerr << "challenge.cpp: key is null!" << std::endl;
    ;
  }
  std::cerr << "challenge.cpp: key = ";
  BN_print_fp(stderr, key);
  std::cerr << std::endl;
  uint8_t *key_bin = (uint8_t *)malloc(sizeof(elliptic_curve256_scalar_t));
  memset(key_bin, 0, sizeof(elliptic_curve256_scalar_t));
  BN_bn2bin(key, key_bin);
  auto key_vec = std::vector<uint8_t>(
      key_bin, &key_bin[sizeof(elliptic_curve256_scalar_t)]);

  object jo;
  while (true) {
    jo = {
        {"choice", "submit_key"},
    };
    jo.emplace("guess", json::value_from(key_vec));
    out() << jo << std::endl;
    std::string line;
    std::getline(std::cin, line);
    if (!line.empty()) {
      std::cerr << line << std::endl;
    }
  }
}
