# Documentation: https://docs.brew.sh/Formula-Cookbook
class Aklog < Formula
  desc "Android & HarmonyOS developer's Swiss Army Knife for Log"
  homepage "https://github.com/wswenyue/aklog"
  version "#_version_#"

  depends_on "python"

  on_macos do
    on_arm do
      url "#_url_darwin_arm64_#"
      sha256 "#_sha256_darwin_arm64_#"
    end
    on_intel do
      url "#_url_darwin_x86_64_#"
      sha256 "#_sha256_darwin_x86_64_#"
    end
  end

  def install
    libexec.install Dir["*"]
    bin.install libexec/"aklog" => "aklog"
    inreplace bin/"aklog", "exe_path", libexec.to_s
    python = Formula["python"].opt_bin/"python3"
    inreplace bin/"aklog", "python3 -m aklog", "#{python} -m aklog"
    inreplace bin/"aklog", "python -m aklog", "#{python} -m aklog"
  end

  def post_install
    return unless OS.mac?

    lib_root = libexec/"lib"
    system "/usr/bin/xattr", "-dr", "com.apple.quarantine", lib_root if lib_root.exist?

    # Sign dylibs first; install_name changes invalidate upstream signatures.
    Dir.glob("#{libexec}/lib/**/*.dylib").each do |dylib|
      chmod 0664, dylib
      MachO::Tools.change_dylib_id(dylib, "@rpath/#{File.basename(dylib)}")
      MachO.codesign!(dylib)
      chmod 0444, dylib
    end

    # hdc loads libusb_shared.dylib; adb/hdc must be ad-hoc signed to run on macOS.
    %w[adb hdc].each do |name|
      Dir.glob("#{libexec}/lib/**/#{name}").each do |executable|
        next unless File.file?(executable)

        MachO.codesign!(executable)
      end
    end
  end

  test do
    system bin/"aklog", "--version"
  end

end
