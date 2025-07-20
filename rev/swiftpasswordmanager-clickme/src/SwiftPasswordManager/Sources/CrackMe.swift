extension String {
    func h() -> UInt64 {
        var hash1: UInt64 = 0x811c9dc5
        var hash2: UInt64 = 0x01000193
        for (index, char) in self.utf8.enumerated() {
            let byte = UInt64(char)
            hash1 = ((hash1 << 7) | (hash1 >> 57)) ^ byte
            hash2 = hash2 &* 33 &+ byte &* UInt64(index + 1)
        }
        return hash1 ^ (hash2 << 32 | hash2 >> 32)
    }
}

// DUCTF{cho05iNg_A_p4s5W0rd_15_h4Rd...}
@inline(__always)
func checkCrackMePassword(s: String) -> Bool {
    guard s.hasPrefix("DU") && s.hasSuffix(".}") else { return false }
    guard s[s.index(s.startIndex, offsetBy: 2)] == "C" else { return false }
    guard s[s.index(s.startIndex, offsetBy: 3)] == "T" else { return false }
    guard s[s.index(s.startIndex, offsetBy: 4)] == "F" else { return false }
    guard s[s.index(s.startIndex, offsetBy: 5)] == "{" else { return false }
    let password = String(s.dropFirst(6).dropLast(2))
    guard password.count == 29 else { return false }

    // flag[28] == "."
    guard password.last == "." else { return false }

    let f2 = password[password.index(password.startIndex, offsetBy: 2)]
    let f6 = password[password.index(password.startIndex, offsetBy: 6)]
    let f8 = password[password.index(password.startIndex, offsetBy: 8)]

    guard password.h() & 0xffffffff == 3633363637 else { return false }
    guard String(password.reversed()).h() >> 32 == 2161988486 else { return false }

    let choosingRange = password.startIndex..<password.index(password.startIndex, offsetBy: 8)
    let choosingReversed = String(password[choosingRange].reversed())
    let everyOtherChar = String(choosingReversed.enumerated().compactMap { index, char in
        index % 2 == 0 ? char : nil
    })

    // flag[7] == "g"
    guard everyOtherChar.first == "g" else { return false }

    // flag[5] == "i"
    guard everyOtherChar[everyOtherChar.index(everyOtherChar.startIndex, offsetBy: 1)].asciiValue! ^ 0xaa == 195 else { return false }

    // flag[3] == "0"
    guard everyOtherChar[everyOtherChar.index(everyOtherChar.startIndex, offsetBy: 2)].asciiValue! + 111 == 159 else { return false }

    // flag[1] == "h"
    guard everyOtherChar[everyOtherChar.index(everyOtherChar.startIndex, offsetBy: 3)].asciiValue! & 1 == 0 else { return false }
    guard String(Character(UnicodeScalar((everyOtherChar[everyOtherChar.index(everyOtherChar.startIndex, offsetBy: 3)].asciiValue! + everyOtherChar.first!.asciiValue!)/2))) == "g" else { return false }

    // flag[0] == "c"
    guard password.first == "c" else { return false }

    // flag[4] == "5", flag[7] == "g"
    let every3rdFrom1 = String(password.enumerated().compactMap { index, char in
        (index + 2) % 3 == 0 && index >= 2 && index <= 7 ? char : nil
    })
    guard every3rdFrom1 == "5g" else { return false }

    // flag[27] == "."
    guard password[password.index(password.startIndex, offsetBy: 27)] == "." else { return false }

    // flag[1] == "h", flag[4] == "5", flag[9] == "A", flag[16] == "0", flag[25] == "R"
    let squareChars = (1...5).compactMap { pos -> UInt64? in
        let pos2 = pos * pos
        guard pos2 < password.count else { return nil }
        let index = password.index(password.startIndex, offsetBy: pos2)
        return String(password[index]).h()
    }
    guard squareChars == [
        2377957896207917800,
        2377958226920399541,
        2377958278460007105,
        2377958205445563056,
        2377957801718637266
    ] else { return false }

    let f14 = password[password.index(password.startIndex, offsetBy: 14)]
    let f15 = password[password.index(password.startIndex, offsetBy: 15)]
    let f24 = password[password.index(password.startIndex, offsetBy: 24)]

    // flag[14] == "5", flag[15] == "W", flag[24] == "4"
    let v14 = UInt16(f14.asciiValue!)
    let v15 = UInt16(f15.asciiValue!)
    let v24 = UInt16(f24.asciiValue!)
    guard 1*v14 + 2*v15 + 3*v24 == 383 else { return false }
    guard 4*v14 + 5*v15 + 6*v24 == 959 else { return false }
    guard 9*v14 + 8*v15 + 9*v24 == 1641 else { return false }

    // flag[10,11,12,13], flag[20,21,22,23]
    let firstRange = password.dropFirst(10).prefix(4)
    let secondRange = password.dropFirst(20).prefix(4)
    let interleaved = String(zip(firstRange, secondRange).flatMap { [$0, $1] }.reversed())
    guard interleaved == "hs_45p1_" else { return false }

    // flag[26] == "d"
    guard password[password.index(password.startIndex, offsetBy: 26)] == "d" else { return false }

    // flag[16,17,18,19]
    let passwordSubrange = password.index(password.startIndex, offsetBy: 16)..<password.index(password.startIndex, offsetBy: 20)
    let passwordPart = String(password[passwordSubrange])
    var swapped = ""
    for i in stride(from: 0, to: passwordPart.count - 1, by: 2) {
        let idx1 = passwordPart.index(passwordPart.startIndex, offsetBy: i)
        let idx2 = passwordPart.index(passwordPart.startIndex, offsetBy: i + 1)
        swapped += String(Character(UnicodeScalar(passwordPart[idx2].asciiValue! - 1))) + String(Character(UnicodeScalar(passwordPart[idx1].asciiValue! + 1)))
    }
    guard swapped == "q1^e" else { return false }

    // flag[2] == "o", flag[6] == "N", flag[8] == "_"
    let v2 = UInt16(f2.asciiValue!)
    let v6 = UInt16(f6.asciiValue!)
    let v8 = UInt16(f8.asciiValue!)
    guard 1*v2 + 2*v6 + 3*v8 == 552 else { return false }
    guard 4*v2 + 5*v6 + 6*v8 == 1404 else { return false }
    guard 6*v2 + 8*v6 + 9*v8 == 2145 else { return false }

    return true
}
