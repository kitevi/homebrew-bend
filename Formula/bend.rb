class Bend < Formula
  desc "Programming language with dependent types and parallel execution"
  homepage "https://bend-lang.com"
  license "Apache-2.0"

  depends_on :macos

  on_macos do
    on_arm do
      url "https://github.com/bendlang/bend/releases/download/v2.0.24/bend-2.0.24-darwin-arm64.tar.gz"
      sha256 "b17380ac7b8fce5c5c0250d23c9bb6d99cc9737bfca8a9e5428e051325926e1e"
    end

    on_intel do
      url "https://github.com/bendlang/bend/releases/download/v2.0.24/bend-2.0.24-darwin-x64.tar.gz"
      sha256 "2ec76dd0ad295f4966cf46318ad87ff59a070195a7ede7560cafc564db232015"
    end
  end

  def install
    libexec.install "bin", "bend2", "guide"
    bin.install_symlink libexec/"bin/bend"
  end

  def caveats
    <<~EOS
      Upgrade with `brew upgrade kitevi/bend/bend`, not `bend update`.
      The upstream updater creates a separate installation outside Homebrew.

      To disable Bend's daily update check:
        export BEND_NO_TELEMETRY=1

      Native compilation requires a compatible Clang toolchain.
    EOS
  end

  test do
    ENV["BEND_NO_TELEMETRY"] = "1"
    assert_equal "bend #{version}", shell_output("#{bin}/bend version").strip
    assert_match "Nat", shell_output("#{bin}/bend base")
    assert_predicate shell_output("#{bin}/bend guide").strip, :present?

    (testpath/"smoke.bend").write <<~EOS
      import Base

      def main() -> IO(Unit):
        IO.print("Hello, Homebrew!")
    EOS
    system bin/"bend", testpath/"smoke.bend", "--check-only"
    assert_match "Hello, Homebrew!", shell_output("#{bin}/bend #{testpath}/smoke.bend")
  end
end
