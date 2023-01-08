import os, sys,shutil
import subprocess

def find_and_replace(filename,old,new):
	with open(filename,"w") as f:
		f.write(open("filename","r").read().replace(old,new))

environment=os.environ.copy()
root_path=os.path.dirname(__file__)
os.chdir(root_path)

options_dict={}

for i in range(1,len(sys.argv)):
	arg=sys.argv[i]
	if not arg.startswith('--'):
		continue
	else:
		arg=arg.removeprefix('--')

	arg=arg.split('=')

	if len(arg)==1:
		arg.append(['download','configure','build'])
	else:
		arg[1]=arg[1].split(',')
	options_dict[arg[0]]=arg[1]

for directory in ["build/qemu", "source"]:
	os.makedirs(os.path.join(root_path,directory),exist_ok=True)

def git_clone(url, branch="",cwd=None):
	subprocess.run(["git","clone","--depth=1",'--recurse-submodules']+(["--branch" ,branch] if branch else [])+[url],cwd=cwd)

if "--depot" in sys.argv:
	git_clone("https://chromium.googlesource.com/chromium/tools/depot_tools.git")

for repo in ["angle","libepoxy","virglrenderer","qemu"]:
	if (repo in options_dict) and ('download' in options_dict[repo]):
		git_clone(f"https://github.com/akihikodaki/{repo}.git","macos","source")

if '--dependencies' in sys.argv:
	subprocess.run(["sudo","port","install","meson","ninja"])
	subprocess.run(["brew","install","glib","pkgconfig"])

if "angle" in options_dict:
	environment["DEPOT_TOOLS_UPDATE"]='0'
	environment["PATH"]=os.path.join(os.getcwd(),"depot_tools")+os.pathsep+environment["PATH"]

	os.chdir("source/angle")
	if 'download' in options_dict['angle']:
		import textwrap
		subprocess.run(["scripts/bootstrap.py"],env=environment)
		subprocess.run(["gclient","sync","-D","-j12","--no-history","--shallow"],env=environment)
		find_and_replace("build/mac/find_sdk.py","best_sdk = sorted(sdks, key=parse_version)[0]","best_sdk = sorted(sdks, key=parse_version)[-1]")
		find_and_replace("build/mac/find_sdk.py","Platforms/MacOSX.platform/Developer/SDKs","SDKs")
		find_and_replace("build/config/apple/sdk_info.py","def FillXcodeVersion(settings, developer_dir):",
			textwrap.dedent("""
			def FillXcodeVersion(settings, developer_dir):
				settings['xcode_version']='11.2.0'
				settings['xcode_build']='11.2.0'
				return
			"""))
	if 'configure' in options_dict['angle']:
		subprocess.run(["gn","gen", "--args=is_debug=false angle_build_tests=false", "../../build/angle"],env=environment)
	os.chdir("../..")
	if 'build' in options_dict['angle']:
		subprocess.run(["ninja","-j4","-C","build/angle"])

if "libepoxy" in options_dict:
	if 'configure' in options_dict['libepoxy']:
		subprocess.run(["meson", f"-Dc_args=-I{os.getcwd()}/source/angle/include","-Degl=yes", "-Dx11=false", f"--prefix={os.getcwd()}","build/libepoxy","source/libepoxy"])

	if 'build' in options_dict['libepoxy']:
		subprocess.run(["meson","install","-C","build/libepoxy"])

if "virglrenderer" in options_dict:
	if 'configure' in options_dict['virglrenderer']:
		subprocess.run(["meson", f"-Dc_args=-I{os.getcwd()}/source/angle/include", f"--pkg-config-path={os.getcwd()}/lib/pkgconfig", f"--prefix={os.getcwd()}","build/virglrenderer","source/virglrenderer"])
	if 'build' in options_dict['virglrenderer']:
		subprocess.run(["meson","install","-C","build/virglrenderer"])

if 'qemu' in options_dict:
	os.chdir("build/qemu")
	import textwrap
	qemu_flags=f"""
	--disable-bsd-user
	--disable-guest-agent
	--disable-gnutls
	--enable-curses
	--disable-libssh
	--disable-nettle
	--disable-lzo
	--disable-snappy
	--disable-zstd
	--extra-cflags=-DNCURSES_WIDECHAR=1
	--target-list=aarch64-softmmu
	--extra-cflags=-I{os.getcwd()}/../../source/angle/include
	--extra-ldflags=-L{os.getcwd()}/../angle
	--extra-ldflags=-L/opt/local/lib
	--extra-cflags=-I/opt/local/include
	--prefix={os.getcwd()}/../..
	--disable-sdl
	--disable-gtk
	--disable-vde
	--disable-gio
	--enable-cocoa
	--disable-curl"""
	qemu_flags=textwrap.dedent(qemu_flags).splitlines()
	environment["PKG_CONFIG_PATH"]=os.getcwd()+"/../../lib/pkgconfig"
	if 'configure' in options_dict['qemu']:
		subprocess.run(["../../source/qemu/configure"]+qemu_flags,env=environment)

	if 'build' in options_dict['qemu']:
		subprocess.run(["meson","install"])
		#subprocess.run(["make","install","-j8"])

if '--clean' in sys.argv:
	for directory in ['build','source','depot_tools']:
		if os.path.isdir(directory):
			shutil.rmtree(directory)
	for directory in ['.vpython-root','.vpython_cipd_cache']:
		subprocess.run(["sudo","rm","-rf",os.path.expanduser('~')+'/'+directory])
		
	subprocess.run(["sudo","port","uninstall","meson","ninja"])
	subprocess.run(["brew","uninstall","glib","pkgconfig"])
