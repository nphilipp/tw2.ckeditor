import os
from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
from setuptools.command.develop import develop
from shutil import rmtree
from subprocess import call
import json

from distutils import log


class generate_files_mixin(object):

    here = os.path.dirname(__file__)

    ckdir = 'ckeditor'
    pymodroot = os.path.join("tw2", "ckeditor")
    staticdir = os.path.join(pymodroot, "static")

    ckbuilddir = os.path.join(ckdir, "dev/builder")
    ckbuildscript = os.path.join(ckbuilddir, "build.sh")

    ckversion = json.load(open(os.path.join(ckdir, "package.json")))['version']
    cktarball = os.path.join(
        ckbuilddir, "release", "ckeditor_{}_dev.tar.gz".format(ckversion))

    ckdistdir = os.path.join(here, staticdir, "ckeditor")
    ckdistmindir = os.path.join(here, staticdir, "ckeditor-min")

    @property
    def ckversion(self):
        if not hasattr(generate_files_mixin, '_ckversion'):
            with open(os.path.join(self.ckdir, 'package.json')) as package_json:
                jsondata = json.load(package_json)
                generate_files_mixin._ckversion = jsondata['version']
        return generate_files_mixin._ckversion

    @property
    def cktarball(self):
        return os.path.join(
            self.ckbuilddir, "release",
            "ckeditor_{}_dev.tar.gz".format(self.ckversion))

    def generate_distribution(self):
        import jsmin, csscompressor

        log.info("Building JS distribution")
        call((
            self.ckbuildscript,
            "--leave-js-unminified", "--leave-css-unminified"))

        log.info("Extracting distribution")
        if os.path.exists(self.ckdistdir):
            rmtree(self.ckdistdir)
        os.makedirs(self.staticdir)
        call(("tar", "-C", self.staticdir, "-xf", self.cktarball))

        log.info("Converting to purely LF line endings")
        for path, dirs, files in os.walk(self.ckdistdir):
            for f in files:
                fpath = os.path.join(path, f)
                name, ext = os.path.splitext(f)
                ext = ext if not ext else ext[1:]
                if not os.path.isfile(fpath) or os.path.islink(fpath) or (
                        name != 'LICENSE' and ext not in (
                            'js', 'css', 'md', 'html', 'json', 'svg', 'txt')):
                    continue
                tmppath = fpath + ".lfconvert"
                with open(fpath) as f, open(tmppath, "w", newline="\n") as c:
                    c.write(f.read())
                origstat = os.stat(fpath)
                tmpstat = os.stat(tmppath)
                if origstat.st_size != tmpstat.st_size:
                    os.rename(tmppath, fpath)
                else:
                    os.unlink(tmppath)

        log.info("Minifying/compressing distribution")
        if os.path.exists(self.ckdistmindir):
            rmtree(self.ckdistmindir)
        topdepth = len(self.ckdistdir.split(os.path.sep))
        for srcpath, dirs, files in os.walk(self.ckdistdir):
            # don't copy samples to minified distribution
            if srcpath == self.ckdistdir:
                dirs.remove('samples')

            spcomps = srcpath.split(os.path.sep)
            destpath = os.path.join(self.ckdistmindir, *spcomps[topdepth:])
            if not os.path.exists(destpath):
                os.mkdir(destpath)
            for f in files:
                sfpath = os.path.join(srcpath, f)
                dfpath = os.path.join(destpath, f)
                dummy, ext = os.path.splitext(f)
                if ext == '.js':
                    with open(sfpath) as s, open(dfpath, "w") as d:
                        d.write(jsmin.jsmin(s.read()))
                elif ext == '.css':
                    with open(sfpath) as s, open(dfpath, "w") as d:
                        d.write(csscompressor.compress(s.read()))
                else:
                    os.link(sfpath, dfpath)


class my_build_py(build_py, generate_files_mixin):

    def run(self):
        if not self.dry_run:
            self.generate_distribution()
        build_py.run(self)


class my_develop(develop, generate_files_mixin):

    def install_for_development(self):
        self.generate_distribution()
        develop.install_for_development(self)

    def uninstall_link(self):
        develop.uninstall_link(self)

        paths = self.paths(self.here, self.here)

        for x in ('ckeditor', 'ckeditor-min'):
            log.info("removing generated files: {}".format(paths[x]))
            rmtree(paths[x])


def find_files(*paths_dirnames):
    all_files = set()

    for path, dirname in paths_dirnames:
        files = set()
        for dpath, dnames, fnames in os.walk(path):
            files.update(
                x for x in (os.path.join(dpath, y) for y in fnames)
                if os.path.isfile(x))
        cutchars = len(path)
        fnames = set(dirname + f[cutchars:] for f in files)
        all_files.update(fnames)

    return sorted(all_files)

if __name__ == '__main__':
    setup(
        name='tw2.ckeditor',
        version='0.1',
        description="ToscaWidgets 2 wrapper for CKEditor",
        author="Nils Philippsen",
        author_email="nils@tiptoe.de",
        #url=
        #download_url=
        setup_requires=["jsmin", "csscompressor"],
        install_requires=["tw2.core >= 2.0", "tw2.forms >= 2.0"],
        packages=find_packages(),
        namespace_packages=['tw2', 'tw2.ckeditor'],
        zip_safe=False,
        include_package_data=True,
        #test_suite='nose.collector'
        package_data={'tw2.ckeditor': find_files(
            ("tw2/ckeditor/static", "static"))},
        entry_points="""
            [tw2.widgets]
            widgets = tw2.ckeditor
        """,
        keywords=['tw2.widgets'],
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Environment :: Web Environment",
            "Environment :: Web Environment :: ToscaWidgets",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Software Development :: Widget Sets",
            "Intended Audience :: Developers",
            "Operating System :: OS Independent",
            "Programming Language :: Python",
        ],
        cmdclass={
            'build_py': my_build_py,
            'develop': my_develop,
            }
    )
