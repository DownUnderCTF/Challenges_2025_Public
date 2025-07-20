#ifndef SETUP_H_
#define SETUP_H_

#include "cosigner/cmp_ecdsa_online_signing_service.h"
#include "cosigner/cmp_setup_service.h"
#include "crypto/GFp_curve_algebra/GFp_curve_algebra.h"

using namespace fireblocks::common::cosigner;

template <typename T> std::string HexStr(const T itbegin, const T itend) {
  std::string rv;
  static const char hexmap[16] = {'0', '1', '2', '3', '4', '5', '6', '7',
                                  '8', '9', 'a', 'b', 'c', 'd', 'e', 'f'};
  rv.reserve((itend - itbegin) * 3);
  for (T it = itbegin; it < itend; ++it) {
    unsigned char val = (unsigned char)(*it);
    rv.push_back(hexmap[val >> 4]);
    rv.push_back(hexmap[val & 15]);
  }

  return rv;
}

class setup_persistency
    : public fireblocks::common::cosigner::cmp_setup_service::setup_key_persistency {

public:
  std::string dump_key(const std::string &key_id) {
    auto it = _keys.find(key_id);
    if (it == _keys.end())
      throw cosigner_exception(cosigner_exception::BAD_KEY);
    return HexStr(it->second.private_key,
                  &it->second.private_key[sizeof(elliptic_curve256_scalar_t)]);
  }

  void load_key(const std::string &key_id, cosigner_sign_algorithm &algorithm,
                elliptic_curve256_scalar_t &private_key) const {
    auto it = _keys.find(key_id);
    if (it == _keys.end())
      throw cosigner_exception(cosigner_exception::BAD_KEY);
    memcpy(private_key, it->second.private_key, sizeof(elliptic_curve256_scalar_t));
    algorithm = it->second.algorithm;
  };
private:
  bool key_exist(const std::string &key_id) const {
    return _keys.find(key_id) != _keys.end();
  };
  const std::string get_tenantid_from_keyid(const std::string &key_id) const {
    return TENANT_ID;
  };
  void load_key_metadata(const std::string &key_id,
                         fireblocks::common::cosigner::cmp_key_metadata &metadata,
                         bool full_load) const {
    auto it = _keys.find(key_id);
    if (it == _keys.end())
      throw cosigner_exception(cosigner_exception::BAD_KEY);
    metadata = it->second.metadata.value();
  };

  void load_auxiliary_keys(const std::string &key_id,
                           fireblocks::common::cosigner::auxiliary_keys &aux) const {
    auto it = _keys.find(key_id);
    if (it == _keys.end())
      throw cosigner_exception(cosigner_exception::BAD_KEY);
    aux = it->second.aux_keys;
  };
  void store_key(const std::string &key_id, cosigner_sign_algorithm algorithm,
                 const elliptic_curve256_scalar_t &private_key, uint64_t ttl = 0) {
    auto &info = _keys[key_id];
    memcpy(info.private_key, private_key, sizeof(elliptic_curve256_scalar_t));
    info.algorithm = algorithm;
  };
  void store_key_metadata(const std::string &key_id,
                          const fireblocks::common::cosigner::cmp_key_metadata &metadata,
                          bool allow_override) {
    auto &info = _keys[key_id];
    if (!allow_override && info.metadata)
      throw cosigner_exception(cosigner_exception::INTERNAL_ERROR);
    info.metadata = metadata;
  };
  void store_auxiliary_keys(const std::string &key_id,
                            const fireblocks::common::cosigner::auxiliary_keys &aux) {
    auto &info = _keys[key_id];
    info.aux_keys = aux;
  };
  void store_keyid_tenant_id(const std::string &key_id, const std::string &tenant_id) {};
  void store_setup_data(const std::string &key_id,
                        const fireblocks::common::cosigner::setup_data &metadata) {
    _setup_data[key_id] = metadata;
  };
  void load_setup_data(const std::string &key_id,
                       fireblocks::common::cosigner::setup_data &metadata) {
    metadata = _setup_data[key_id];
  };
  void store_setup_commitments(
      const std::string &key_id,
      const std::map<uint64_t, fireblocks::common::cosigner::commitment> &commitments) {
    if (_commitments.find(key_id) != _commitments.end())
      throw cosigner_exception(cosigner_exception::INTERNAL_ERROR);
    _commitments[key_id] = commitments;
  };
  void load_setup_commitments(
      const std::string &key_id,
      std::map<uint64_t, fireblocks::common::cosigner::commitment> &commitments) {
    commitments = _commitments[key_id];
  };
  void delete_temporary_key_data(const std::string &key_id, bool delete_key = false) {
    _setup_data.erase(key_id);
    _commitments.erase(key_id);
    if (delete_key)
      _keys.erase(key_id);
  };

  struct key_info {
    cosigner_sign_algorithm algorithm;
    elliptic_curve256_scalar_t private_key;
    std::optional<fireblocks::common::cosigner::cmp_key_metadata> metadata;
    fireblocks::common::cosigner::auxiliary_keys aux_keys;
  };

  std::map<std::string, key_info> _keys;
  std::map<std::string, fireblocks::common::cosigner::setup_data> _setup_data;
  std::map<std::string, std::map<uint64_t, fireblocks::common::cosigner::commitment>>
      _commitments;
};

struct setup_info {
  setup_info(uint64_t id, setup_persistency &persistency)
      : platform_service(id), setup_service(platform_service, persistency) {}
  platform platform_service;
  cmp_setup_service setup_service;
};

typedef std::map<uint64_t, setup_persistency> players_setup_info;

#endif // SETUP_H_
