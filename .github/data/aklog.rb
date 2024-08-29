# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://www.rubydoc.info/github/Homebrew/brew/master/Formula
# PLEASE REMOVE ALL GENERATED COMMENTS BEFORE SUBMITTING YOUR PULL REQUEST!
class Aklog < Formula
  desc "Android or Harmony developer's Swiss Army Knife for Log"
  homepage "https://github.com/wswenyue/aklog"
  url "#_url_#"
  sha256 "#_sha256_#"
  version '#_version_#'

  def install
    libexec.install Dir["*"]
    bin.install libexec/"aklog" => "aklog"
    bin.install libexec/"hilog" => "hilog"
    inreplace bin/"aklog", "exe_path", "#{libexec}"
    inreplace bin/"hilog", "exe_path", "#{libexec}"
  end

  test do
    system bin/"aklog", "--version"
    system bin/"hilog", "--version"
  end

end