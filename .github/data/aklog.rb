# Documentation: https://docs.brew.sh/Formula-Cookbook
class Aklog < Formula
  desc "Android & HarmonyOS developer's Swiss Army Knife for Log"
  homepage "https://github.com/wswenyue/aklog"
  url "#_url_#"
  sha256 "#_sha256_#"
  version '#_version_#'

  depends_on "python@3.12"

  def install
    libexec.install Dir["*"]
    bin.install libexec/"aklog" => "aklog"
    inreplace bin/"aklog", "exe_path", libexec.to_s
    python = Formula["python@3.12"].opt_bin/"python3.12"
    inreplace bin/"aklog", "python3 -m aklog", "#{python} -m aklog"
    inreplace bin/"aklog", "python -m aklog", "#{python} -m aklog"
  end

  def post_install
    Dir.glob("#{libexec}/lib/**/*.dylib").each do |dylib|
      chmod 0664, dylib
      MachO::Tools.change_dylib_id(dylib, "@rpath/#{File.basename(dylib)}")
      MachO.codesign!(dylib) if Hardware::CPU.arm?
      chmod 0444, dylib
    end
  end

  test do
    system bin/"aklog", "--version"
  end

end
