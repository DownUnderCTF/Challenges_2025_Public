#ifndef SIGNING_H_
#define SIGNING_H_

#include "cosigner/cmp_ecdsa_online_signing_service.h"
#include "cosigner/cmp_setup_service.h"
#include "crypto/GFp_curve_algebra/GFp_curve_algebra.h"
#include <shared_mutex>

using namespace fireblocks::common::cosigner;

constexpr int MPC_CMP_ONLINE_VERSION = 6;

// Performs CRUD on an inmemory map from txid -> cmp_signing_metadata
class online_signing_persistency
    : public cmp_ecdsa_online_signing_service::signing_persistency {
  void store_cmp_signing_data(const std::string &txid,
                              const cmp_signing_metadata &data) override {
    std::unique_lock lock(_mutex);
    if (_metadata.find(txid) != _metadata.end())
      throw cosigner_exception(cosigner_exception::INVALID_TRANSACTION);
    _metadata[txid] = data;
  }

  void load_cmp_signing_data(const std::string &txid,
                             cmp_signing_metadata &data) const override {
    std::shared_lock lock(_mutex);
    auto it = _metadata.find(txid);
    if (it == _metadata.end())
      throw cosigner_exception(cosigner_exception::INVALID_TRANSACTION);
    data = it->second;
  }

  void update_cmp_signing_data(const std::string &txid,
                               const cmp_signing_metadata &data) override {
    std::unique_lock lock(_mutex);
    auto it = _metadata.find(txid);
    if (it == _metadata.end())
      throw cosigner_exception(cosigner_exception::INVALID_TRANSACTION);
    it->second = data;
  }

  void delete_signing_data(const std::string &txid) override {
    std::unique_lock lock(_mutex);
    _metadata.erase(txid);
  }

  mutable std::shared_mutex _mutex;

  std::map<std::string, cmp_signing_metadata> _metadata;
};

// Structure representing everything a player needs to do signatures
struct signing_info {
  signing_info(uint64_t id, const cmp_key_persistency &persistency)
      : platform_service(id),
        signing_service(platform_service, persistency, signing_persistency) {}
  platform platform_service; // platform specific RNG
  online_signing_persistency signing_persistency;
  cmp_ecdsa_online_signing_service signing_service;
};

#endif // SIGNING_H_
