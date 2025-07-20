import Foundation
import Crypto

class CryptoHelper {
  @inline(__always)
  static func deriveKey(from password: String, salt: Data) -> SymmetricKey? {
    guard let passwordData = password.data(using: .utf8) else { return nil }

    let iterations = 0xaaaa
    var key = passwordData

    for _ in 0..<iterations {
      key = Data(SHA256.hash(data: key + salt))
    }

    return SymmetricKey(data: key)
  }

  @inline(__always)
  static func encrypt(data: Data, key: SymmetricKey) -> (ciphertext: Data, nonce: Data, tag: Data)?
  {
    do {
      let nonce = AES.GCM.Nonce()
      let sealed = try AES.GCM.seal(data, using: key, nonce: nonce)

      let ciphertext = sealed.ciphertext
      let tag = sealed.tag
      let nonceData = Data(nonce)

      return (Data(ciphertext), nonceData, Data(tag))
    } catch {
      print("Encryption error: \(error)")
      return nil
    }
  }

  // static func decrypt(ciphertext: Data, key: SymmetricKey, nonce: Data, tag: Data) -> Data? {
  //   do {
  //     let gcmNonce = try AES.GCM.Nonce(data: nonce)
  //     let sealedBox = try AES.GCM.SealedBox(
  //       nonce: gcmNonce,
  //       ciphertext: ciphertext,
  //       tag: tag
  //     )
  //
  //     let decrypted = try AES.GCM.open(sealedBox, using: key)
  //     return decrypted
  //   } catch {
  //     print("Decryption error: \(error)")
  //     return nil
  //   }
  // }

  @inline(__always)
  static func generateSalt() -> Data {
    var bytes = [UInt8](repeating: 0, count: 32)
    for i in 0..<32 {
      bytes[i] = UInt8.random(in: 0...255)
    }
    return Data(bytes)
  }
}
