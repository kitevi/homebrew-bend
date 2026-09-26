class Bend < Formula
  desc "Programming language with dependent types and parallel execution"
  homepage "https://bend-lang.com"
  license "Apache-2.0"

  depends_on :macos

  on_macos do
    on_arm do
      url "https://github.com/bendlang/bend/releases/download/v2.0.29/bend-2.0.29-darwin-arm64.tar.gz"
      sha256 "40bff13c8e33ab65dfe3c09b1863c1f13035b1cf3badafc340a010766ccaf895"
    end

    on_intel do
      url "https://github.com/bendlang/bend/releases/download/v2.0.29/bend-2.0.29-darwin-x64.tar.gz"
      sha256 "3a8abed360f1fe6b22ac55c358230ce71c8ad5ffd3b1f104764429b987a61d02"
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
