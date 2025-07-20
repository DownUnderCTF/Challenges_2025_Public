#include <boost/beast/core/detail/base64.hpp>

#include <boost/json.hpp>
#include <iostream>

namespace json = boost::json;
namespace b64 = boost::beast::detail::base64;

json::value read_json_object() {
  std::string line;
  json::stream_parser parser;
  do {
    getline(std::cin, line);
    parser.write_some(line);
  } while (!parser.done());

  return parser.release();
}

namespace boost {
namespace json {
template <> struct is_sequence_like<std::vector<std::uint8_t>> : std::false_type {};
template <typename T> struct is_sequence_like<std::map<std::uint64_t, T>> : std::false_type {};

} // namespace json
} // namespace boost

namespace std {
using bytes = std::vector<std::uint8_t>;

template <typename T>
void tag_invoke(json::value_from_tag, json::value &jv, std::map<uint64_t, T> const &c) {
  json::object jo;

  for (auto &[k, v] : c) {
    jo.emplace(std::to_string(k), json::value_from(v));
  }

  jv = jo;
}

template <typename T>
std::map<uint64_t, T> tag_invoke(json::value_to_tag<std::map<uint64_t, T>>,
                                 json::value const &jv) {
  std::map<uint64_t, T> c;
  json::object jo = jv.as_object();
  for (auto &[k, v] : jo) {
    c.emplace(std::stoi(k), json::value_to<T>(v));
  }

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, bytes const &v) {
  std::string enc;
  enc.resize(b64::encoded_size(v.size()));
  b64::encode(enc.data(), v.data(), v.size());
  jv = enc;
}

bytes tag_invoke(json::value_to_tag<bytes>, json::value const &jv) {
  auto const &s = jv.as_string();
  bytes out;
  out.resize(b64::decoded_size(s.size()));
  auto [len, _] = b64::decode(out.data(), s.c_str(), s.size());
  out.resize(len);
  return out;
}
} // namespace std

namespace fireblocks {
namespace common {
namespace cosigner {

void tag_invoke(json::value_from_tag, json::value &jv, const commitment &c) {
  json::object jo;
  std::vector<uint8_t> salt_vec(c.data.salt, &c.data.salt[sizeof(c.data.salt)]),
      commitment_vec(c.data.commitment, &c.data.commitment[sizeof(c.data.commitment)]);

  jo.emplace("salt", json::value_from(salt_vec));
  jo.emplace("commitment", json::value_from(commitment_vec));

  jv = jo;
}

commitment tag_invoke(json::value_to_tag<commitment>, json::value const &jv) {
  commitment c;
  auto salt = json::value_to<byte_vector_t>(jv.as_object().at("salt"));
  auto commitment = json::value_to<byte_vector_t>(jv.as_object().at("commitment"));

  std::copy_n(salt.begin(), std::min(salt.size(), sizeof(c.data.salt)), &c.data.salt[0]);
  std::copy_n(commitment.begin(), std::min(commitment.size(), sizeof(c.data.commitment)),
              &c.data.commitment[0]);

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const setup_decommitment &c) {
  json::object jo;
  std::vector<uint8_t> ack_vec(c.ack, &c.ack[sizeof(c.ack)]),
      seed_vec(c.seed, &c.seed[sizeof(c.seed)]);
  jo.emplace("ack", json::value_from(ack_vec));
  jo.emplace("seed", json::value_from(seed_vec));
  jo.emplace("share", json::value_from(c.share));
  jo.emplace("paillier_public_key", json::value_from(c.paillier_public_key));
  jo.emplace("ring_pedersen_public_key", json::value_from(c.ring_pedersen_public_key));

  jv = jo;
}

setup_decommitment tag_invoke(json::value_to_tag<setup_decommitment>, json::value const &jv) {
  setup_decommitment c;
  json::object jo = jv.as_object();
  auto ack = json::value_to<byte_vector_t>(jo.at("ack"));
  auto seed = json::value_to<byte_vector_t>(jo.at("seed"));
  c.share = json::value_to<public_share>(jo.at("share"));
  c.paillier_public_key = json::value_to<byte_vector_t>(jo.at("paillier_public_key"));
  c.ring_pedersen_public_key =
      json::value_to<byte_vector_t>(jo.at("ring_pedersen_public_key"));

  std::copy_n(ack.begin(), std::min(ack.size(), sizeof(c.ack)), c.ack);
  std::copy_n(seed.begin(), std::min(seed.size(), sizeof(c.seed)), c.seed);

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const public_share &c) {
  json::object jo;
  jo.emplace("X", json::value_from(c.X));
  jo.emplace("schnorr_R", json::value_from(c.schnorr_R));

  jv = jo;
}

public_share tag_invoke(json::value_to_tag<public_share>, json::value const &jv) {
  public_share c;
  c.X = json::value_to<elliptic_curve_point>(jv.as_object().at("X"));
  c.schnorr_R = json::value_to<elliptic_curve_point>(jv.as_object().at("schnorr_R"));
  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const elliptic_curve_point &c) {
  auto c_vec = std::vector<uint8_t>(c.data, &c.data[sizeof(c.data)]);
  jv = json::value_from(c_vec);
}

elliptic_curve_point tag_invoke(json::value_to_tag<elliptic_curve_point>,
                                json::value const &jv) {
  elliptic_curve_point c;
  auto c_vec = json::value_to<std::vector<uint8_t>>(jv);
  std::copy_n(c_vec.begin(), std::min(c_vec.size(), sizeof(c.data)), c.data);

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const elliptic_curve_scalar &c) {
  auto c_vec = std::vector<uint8_t>(c.data, &c.data[sizeof(c.data)]);
  jv = json::value_from(c_vec);
}

elliptic_curve_scalar tag_invoke(json::value_to_tag<elliptic_curve_scalar>,
                                 json::value const &jv) {
  elliptic_curve_scalar c;
  auto c_vec = json::value_to<std::vector<uint8_t>>(jv);
  std::copy_n(c_vec.begin(), std::min(c_vec.size(), sizeof(c.data)), c.data);

  return c;
}


void tag_invoke(json::value_from_tag, json::value &jv, const setup_zk_proofs &c) {
  json::object jo;
  jo.emplace("schnorr_s", json::value_from(c.schnorr_s));
  jo.emplace("paillier_blum_zkp", json::value_from(c.paillier_blum_zkp));
  jo.emplace("ring_pedersen_param_zkp", json::value_from(c.ring_pedersen_param_zkp));

  jv = jo;
}

setup_zk_proofs tag_invoke(json::value_to_tag<setup_zk_proofs>, json::value const &jv) {
  setup_zk_proofs c;
  auto schnorr_s = json::value_to<std::vector<uint8_t>>(jv.as_object().at("schnorr_s"));
  std::copy_n(schnorr_s.begin(), std::min(schnorr_s.size(), sizeof(c.schnorr_s.data)),
              c.schnorr_s.data);

  c.paillier_blum_zkp = json::value_to<byte_vector_t>(jv.as_object().at("paillier_blum_zkp"));
  c.ring_pedersen_param_zkp =
      json::value_to<byte_vector_t>(jv.as_object().at("ring_pedersen_param_zkp"));

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const cmp_mta_message &c) {
  json::object jo;
  jo.emplace("message", json::value_from(c.message));
  jo.emplace("commitment", json::value_from(c.commitment));
  jo.emplace("proof", json::value_from(c.proof));
  jv = jo;
}

cmp_mta_message tag_invoke(json::value_to_tag<cmp_mta_message>, json::value const &jv) {
  cmp_mta_message c;
  c.message = json::value_to<byte_vector_t>(jv.as_object().at("message"));
  c.commitment = json::value_to<byte_vector_t>(jv.as_object().at("commitment"));
  c.proof = json::value_to<byte_vector_t>(jv.as_object().at("proof"));
  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const cmp_mta_request &c) {
  json::object jo;
  jo.emplace("mta", json::value_from(c.mta));
  jo.emplace("mta_proofs", json::value_from(c.mta_proofs));
  jo.emplace("A", json::value_from(c.A));
  jo.emplace("B", json::value_from(c.B));
  jo.emplace("Z", json::value_from(c.Z));

  jv = jo;
}

cmp_mta_request tag_invoke(json::value_to_tag<cmp_mta_request>, json::value const &jv) {
  cmp_mta_request c;

  c.mta = json::value_to<cmp_mta_message>(jv.as_object().at("mta"));
  c.mta_proofs = json::value_to<std::map<uint64_t, byte_vector_t>>(jv.as_object().at("mta_proofs"));
  auto A = json::value_to<byte_vector_t>(jv.as_object().at("A"));
  auto B = json::value_to<byte_vector_t>(jv.as_object().at("B"));
  auto Z = json::value_to<byte_vector_t>(jv.as_object().at("Z"));
  std::copy_n(A.begin(), std::min(A.size(), sizeof(c.A.data)), c.A.data);
  std::copy_n(B.begin(), std::min(B.size(), sizeof(c.B.data)), c.B.data);
  std::copy_n(Z.begin(), std::min(Z.size(), sizeof(c.Z.data)), c.Z.data);

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const cmp_mta_response &c) {
  json::object jo;
  jo.emplace("k_gamma_mta", json::value_from(c.k_gamma_mta));
  jo.emplace("k_x_mta", json::value_from(c.k_x_mta));
  jo.emplace("GAMMA", json::value_from(c.GAMMA));
  jo.emplace("gamma_proofs", json::value_from(c.gamma_proofs));

  jv = jo;
}

cmp_mta_response tag_invoke(json::value_to_tag<cmp_mta_response>, json::value const &jv) {
  cmp_mta_response c;
  json::object jo = jv.as_object();
  c.k_gamma_mta = json::value_to<std::map<uint64_t, cmp_mta_message>>(jo.at("k_gamma_mta"));
  c.k_x_mta = json::value_to<std::map<uint64_t, cmp_mta_message>>(jo.at("k_x_mta"));
  auto GAMMA = json::value_to<byte_vector_t>(jv.as_object().at("GAMMA"));
  std:copy_n(GAMMA.begin(), std::min(GAMMA.size(), sizeof(c.GAMMA.data)), c.GAMMA.data);
  c.gamma_proofs = json::value_to<std::map<uint64_t, byte_vector_t>>(jo.at("gamma_proofs"));

  return c;
}


void tag_invoke(json::value_from_tag, json::value &jv, const cmp_mta_responses &c) {
  json::object jo;
  std::vector<uint8_t> ack_vec(c.ack, &c.ack[sizeof(c.ack)]);
  jo.emplace("ack", json::value_from(ack_vec));
  jo.emplace("response", json::value_from(c.response));

  jv = jo;
}

cmp_mta_responses tag_invoke(json::value_to_tag<cmp_mta_responses>, json::value const &jv) {
  cmp_mta_responses c;
  auto ack = json::value_to<byte_vector_t>(jv.as_object().at("ack"));
  std::copy_n(ack.begin(), std::min(ack.size(), sizeof(c.ack)), c.ack);

  c.response = json::value_to<std::vector<cmp_mta_response>>(jv.as_object().at("response"));
  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const cmp_mta_deltas &c) {
  json::object jo;
  jo.emplace("delta", json::value_from(c.delta));
  jo.emplace("DELTA", json::value_from(c.DELTA));
  jo.emplace("proof", json::value_from(c.proof));

  jv = jo;
}

cmp_mta_deltas tag_invoke(json::value_to_tag<cmp_mta_deltas>, json::value const &jv) {
  cmp_mta_deltas c;
  auto delta = json::value_to<byte_vector_t>(jv.as_object().at("delta"));
  std::copy_n(delta.begin(), std::min(delta.size(), sizeof(c.delta.data)), c.delta.data);
  c.DELTA = json::value_to<elliptic_curve_point>(jv.as_object().at("DELTA"));
  c.proof = json::value_to<byte_vector_t>(jv.as_object().at("proof"));

  return c;
}

void tag_invoke(json::value_from_tag, json::value &jv, const recoverable_signature &c) {
  json::object jo;
  std::vector<uint8_t> r_vec(c.r, &c.r[sizeof(c.r)]), s_vec(c.s, &c.s[sizeof(c.s)]);
  jo.emplace("r", json::value_from(r_vec));
  jo.emplace("s", json::value_from(s_vec));
  jo.emplace("v", json::value_from(c.v));

  jv = jo;
}

} // namespace cosigner
} // namespace common
} // namespace fireblocks
