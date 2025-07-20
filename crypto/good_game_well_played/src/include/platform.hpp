#ifndef PLATFORM_H_
#define PLATFORM_H_

#include "cosigner/cmp_ecdsa_online_signing_service.h"
#include "cosigner/cmp_setup_service.h"
#include "crypto/GFp_curve_algebra/GFp_curve_algebra.h"
#include <openssl/rand.h>

using namespace fireblocks::common::cosigner;

const char *TENANT_ID = "DOWNUNDERCTF";

// Class providing platform services such as randomness and encryption
// We pretty much stub out everything bcs we don't need it
class platform : public platform_service {
public:
  platform(uint64_t id) : _id(id) {}

private:
  void gen_random(size_t len, uint8_t *random_data) const override {
    RAND_bytes(random_data, len);
  }
  uint64_t now_msec() const override {
    return std::chrono::time_point_cast<std::chrono::milliseconds>(
               std::chrono::steady_clock::now())
        .time_since_epoch()
        .count();
  }
  const std::string get_current_tenantid() const override { return TENANT_ID; }
  uint64_t get_id_from_keyid(const std::string &key_id) const override { return _id; }
  void derive_initial_share(const share_derivation_args &derive_from,
                            cosigner_sign_algorithm algorithm,
                            elliptic_curve256_scalar_t *key) const override {
    assert(0);
  }
  byte_vector_t encrypt_for_player(uint64_t id, const byte_vector_t &data) const override {
    return data;
  }
  byte_vector_t decrypt_message(const byte_vector_t &encrypted_data) const override {
    return encrypted_data;
  }
  bool backup_key(const std::string &key_id, cosigner_sign_algorithm algorithm,
                  const elliptic_curve256_scalar_t &private_key,
                  const cmp_key_metadata &metadata, const auxiliary_keys &aux) override {
    return true;
  }
  void start_signing(const std::string &key_id, const std::string &txid,
                     const signing_data &data, const std::string &metadata_json,
                     const std::set<std::string> &players) override {}
  void fill_signing_info_from_metadata(const std::string &metadata,
                                       std::vector<uint32_t> &flags) const override {}
  bool is_client_id(uint64_t player_id) const override { return false; }
  uint64_t _id;
};

#endif // PLATFORM_H_
