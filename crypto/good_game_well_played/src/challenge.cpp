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
                const std::vector<std::vector<uint32_t>> &paths,
                uint64_t my_id) {
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
        keyid, txid, type, data, "", players_str, players_ids, request);
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
    services[my_id]->signing_service.mta_verify(txid, mta_responses, delta);

    object jo;
    jo["cmp_mta_deltas"] = value_from(delta);
    out() << jo << std::endl;

    value jv = read_json_object();
    deltas[!my_id] = value_to<std::vector<cmp_mta_deltas>>(
        jv.as_object().at("cmp_mta_deltas"));
  }
  mta_responses.clear();

  std::map<uint64_t, std::vector<elliptic_curve_scalar>> sis;
  {
    auto &si = sis[my_id];
    services[my_id]->signing_service.get_si(txid, deltas, si);

    object jo;
    jo["sis"] = value_from(si);
    out() << jo << std::endl;

    value jv = read_json_object();
    sis[!my_id] =
        value_to<std::vector<elliptic_curve_scalar>>(jv.as_object().at("sis"));
  }
  deltas.clear();

  std::vector<recoverable_signature> sigs;
  services[my_id]->signing_service.get_cmp_signature(txid, sis, sigs);
  sis.clear();

  object jo;
  array ja;

  std::unique_ptr<elliptic_curve256_algebra_ctx_t,
                  void (*)(elliptic_curve256_algebra_ctx_t *)>
      algebra(elliptic_curve256_new_secp256k1_algebra(),
              elliptic_curve256_algebra_ctx_free);
  for (size_t i = 0; i < count; i++) {
    elliptic_curve256_scalar_t msg;
    assert(data.blocks[i].data.size() == sizeof(elliptic_curve256_scalar_t));
    memcpy(msg, data.blocks[i].data.data(), sizeof(elliptic_curve256_scalar_t));

    object sig_pair;
    sig_pair["signature"] = value_from(sigs);

    PubKey derived_key;
    assert(derive_public_key_generic(algebra.get(), derived_key, pubkey,
                                     data.chaincode, paths[i].data(),
                                     paths[i].size()) == HD_DERIVE_SUCCESS);
    sig_pair["derived_public_key"] = json::value_from(
        std::vector<uint8_t>(derived_key, &derived_key[sizeof(derived_key)]));
    assert(GFp_curve_algebra_verify_signature(
               (GFp_curve_algebra_ctx_t *)algebra->ctx, &derived_key, &msg,
               &sigs[i].r, &sigs[i].s) == ELLIPTIC_CURVE_ALGEBRA_SUCCESS);
    ja.emplace_back(sig_pair);
  }
  jo["signatures"] = ja;
  std::cerr << jo << std::endl;
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

void get_user_choice(players_setup_info &players) {
  value jv = read_json_object();
  string js = jv.at("choice").as_string();
  if (js.compare("submit_key") == 0) {
    byte_vector_t guess = value_to<byte_vector_t>(jv.at("guess"));
    elliptic_curve256_scalar_t private_key;
    cosigner_sign_algorithm algo;
    players[SERVER_ID].load_key(keyid, algo, private_key);

    if (memcmp(private_key, guess.data(), sizeof(elliptic_curve256_scalar_t)) ==
        0) {
      out() << std::getenv("FLAG") << std::endl;
    }

  } else if (js.compare("continue") == 0) {
    return;
  }

  exit(0);
}

int main(int argc, char **argv) {
  out(); // reserve stdout for ourselves, and surpress libcosigner logs

  uint64_t my_id;
  if (argc > 1 && (strcmp(argv[1], "client") == 0)) {
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

  for (;;) {
    try {
      ecdsa_sign(players, ECDSA_SECP256K1, keyid, 1, pubkey, chaincode, {path},
                 my_id);
    } catch (...) {
      // nop
    }

    if (my_id == SERVER_ID) {
      get_user_choice(players);
    } else {
      object jo = {{"choice", "quit"}};
      out() << jo << std::endl;
    }
  }
}
