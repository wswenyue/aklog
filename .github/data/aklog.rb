# Documentation: https://docs.brew.sh/Formula-Cookbook
#                https://www.rubydoc.info/github/Homebrew/brew/master/Formula
# PLEASE REMOVE ALL GENERATED COMMENTS BEFORE SUBMITTING YOUR PULL REQUEST!
class Aklog < Formula
  name "Aklog"
  desc "Android developer's Swiss Army Knife for Log"
  homepage "https://github.com/wswenyue/aklog"
  version "#_version_#"
  url "#_url_#"
  sha256 "#_sha256_#"


  def install
    libexec.install Dir["*"]
    bin.install libexec/"aklog" => "aklog"
    inreplace bin/"aklog", "exe_path", "#{libexec}"
  end

  test do
    system "false"
  end

end