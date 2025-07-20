// swift-tools-version: 5.10

import PackageDescription

let package = Package(
  name: "SwiftPasswordManager",
  platforms: [.macOS(.v10_15), .iOS(.v13), .tvOS(.v13), .macCatalyst(.v13)],
  dependencies: [
    .package(url: "https://github.com/stackotter/swift-cross-ui", branch: "main"),
    .package(url: "https://github.com/stackotter/swift-bundler", branch: "main"),
    .package(url: "https://github.com/apple/swift-crypto", from: "3.0.0"),
  ],
  targets: [
    .executableTarget(
      name: "SwiftPasswordManager",
      dependencies: [
        .product(name: "SwiftCrossUI", package: "swift-cross-ui"),
        .product(name: "DefaultBackend", package: "swift-cross-ui"),
        .product(name: "Crypto", package: "swift-crypto"),
        .product(
          name: "SwiftBundlerRuntime",
          package: "swift-bundler",
          condition: .when(platforms: [.macOS])
        ),
      ]
    )
  ]
)
