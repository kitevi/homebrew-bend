class Bend < Formula
  desc "Programming language with dependent types and parallel execution"
  homepage "https://bend-lang.com"
  license "Apache-2.0"

  depends_on :macos

  on_macos do
    on_arm do
      url "https://github.com/bendlang/bend/releases/download/v2.0.25/bend-2.0.25-darwin-arm64.tar.gz"
      sha256 "c5bb22ba029d5909da9c6db82aa037278a66d1cf8a5572f433879f7dcd866c31"
    end

    on_intel do
      url "https://github.com/bendlang/bend/releases/download/v2.0.25/bend-2.0.25-darwin-x64.tar.gz"
      sha256 "78e70cda4068f83736649c760575f4382259d5817be96d2eb04b9d078d943af0"
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
