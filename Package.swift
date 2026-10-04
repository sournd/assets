// swift-tools-version:5.9
// sournd brand kit for Swift (iOS, macOS): token values, mark files and the brand fonts.
import PackageDescription

let package = Package(
    name: "SourndAssets",
    platforms: [.iOS(.v15), .macOS(.v12)],
    products: [.library(name: "SourndAssets", targets: ["SourndAssets"])],
    targets: [
        .target(
            name: "SourndAssets",
            path: ".",
            exclude: [
                "README.md", "package.json", "index.js", "composer.json", "src", "design", "tools",
                "python", "rust", "pyproject.toml", "docs", "fonts/mark", "fonts/fonts.css",
                "fonts/bricolage-grotesque/OFL.txt", "fonts/instrument-sans/OFL.txt",
                "marks/png",
            ],
            sources: ["swift/SourndAssets"],
            resources: [
                .copy("tokens"),
                .copy("marks/sournd-wordmark-light.svg"),
                .copy("marks/sournd-wordmark-dark.svg"),
                .copy("marks/sournd-icon-full.svg"),
                .copy("marks/sournd-icon-small.svg"),
                .copy("marks/sournd-icon-tiny.svg"),
                .copy("web"),
                .copy("fonts/bricolage-grotesque"),
                .copy("fonts/instrument-sans"),
            ]
        ),
        .testTarget(name: "SourndAssetsTests", dependencies: ["SourndAssets"], path: "swift/Tests"),
    ]
)
