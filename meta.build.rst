================================================
Building and Deploying the MongoDB Documentation
================================================

This document contains more direct instructions for building the
MongoDB documentation.

Requirements
------------

For basic publication and testing:

- GNU Make
- Python
- Git
- Sphinx (documentation management toolchain)
- Pygments (syntax highlighting)
- PyYAML (for the generated tables)

For full publication builds:

- python-argparse
- LaTeX/PDF LaTeX (typically texlive; for building PDFs)
- Common Utilities (rsync, tar, gzip, sed)

Building the Documentation
--------------------------

Clone the repository: ::

     git clone git://github.com/mongodb/docs.git

To build the full publication version of the manual, you will need to
have a function LaTeX tool chain; however, for routine day-to-day
rendering of the documentation you can install a much more minimal
tool chain.

For Routine Builds
~~~~~~~~~~~~~~~~~~

Begin by installing dependencies. On Arch Linux, use the following
command to install the full dependencies: ::

     pacman -S python2-sphinx python2-pygments python2-yaml

On Debian/Ubuntu systems issue the following command: ::

     apt-get install python-sphinx python-yaml python-argparse

To build the documentation issue the following command: ::

     make html

You can find the build output in ``build/<branch>/html``, where
``<branch>`` is the name of your current branch.

For Publication Builds
~~~~~~~~~~~~~~~~~~~~~~

Begin by installing additional dependencies. On Arch Linux, use the
following command to install the full dependencies: ::

     pacman -S texlive-bin texlive-core texlive-latexextra python2-sphinx python2-pygments python2-yaml

On Debian/Ubuntu systems use the following command: ::

     apt-get install python-yaml python-argparse python-sphinx texlive-latex-recommended texlive-latex-recommended

**Note:** *The Debian/Ubuntu dependencies, have not been thoroughly
tested. If you find an additional dependency, please submit a pull
request to modify this document.*

On OS X:

#. You may need to use ``easy_install`` to install ``pip`` using the
   following command if you have not already done so: ::

        easy_install pip

   Alternately, you may be able to replace ``pip`` with
   ``easy_install`` in the next step.

#. Install Sphinx, Docutils, and their dependencies with ``pip`` using
   the following command: ::

        pip install Sphinx Jinja2 Pygments docutils  PyYAML

   ``Jinja2``, ``Pygments``, and ``docutils`` are all dependencies of
   ``Sphinx``.

   .. note::

      As of June 6, 2012 and Sphinx version 1.1.3, you **must**
      compile the MongoDB documentation using the Python 2.x series
      version of Sphinx. There are serious generation problems with
      the Python 3 series version of Sphinx.

#. Install a TeX distribution (for building the PDF.) If you do not
   have a LaTeX installation, use `MacTeX <http://www.tug.org/mactex/2011/>`_

*If you have any corrections to the instructions for these platforms
or you have a dependency list for Fedora, CentOS, Red Hat, or other
related distributions, please submit a pull request to add this
information to this document.*

To build a test version of the Manual, issue the following command: ::

     make publish

This places a complete version of the manual in
"``../public-docs/``" named for the current branch (as of
*2012-03-19*, typically master.)

To publish a new build of the manual, issue the following command: ::

     make push

**Warning:** *This target depends on* ``publish``, *and simply uses*
``rsync`` *to move the content of the* "``../public-docs/``" *to the web
servers. You must have the proper credentials to run these operations.*

*Run* ``publish`` *procedure and thoroughly test the build before pushing
it live.*

Troubleshooting
---------------

If you encounter problems with the build, please contact the `docs
team <mailto:docs@10gen.com>`_, so that we can update this guide
and/or fix the build process.

Build Components and Internals
------------------------------

This section describes the build system for the MongoDB manual,
including the custom components, and the organization of the
production build process, and the implementation and encoding of the
build process.

Tables
~~~~~~

``bin/table_builder.py`` provides a way to generate easy to main
reStructuredText tables, from content stored in YAML
files.

**Rationale**: reStructuredText's default tables are easy to read in
source format, but expensive to maintain, particularly with larger
numbers of columns, because changing widths of column necessitates
reformatting the entire table. reStructuredText does provide a more
simple "list table" format for simple tables, but these tables do not
support more complex multi-line output.

**Solution**: ``table_builder.py`` reads a ``.yaml`` file that
contains three documents:

(*Each document has a ``section`` field that holds the name/type of
the section, that ``table_builder.py`` uses to ensure that the YAML
file is well formed.*)

#. A ``layout`` document that describes the structure the final
   presentation of the table. Contains two field, a ``header`` that
   holds a list of field references, and a ``rows`` field that holds a
   list of lists of field references, for example::

        section: layout
        header: [ meta.header1, meta.header2 ]
        rows:
          - 1: [ content.sql1, content.mongo1 ]
          - 2: [ content.sql2, content.mongo2 ]
          - 3: [ content.sql3, content.mongo3 ]
          - 4: [ content.sql4, content.mongo4 ]

#. A ``meta`` document that holds row, column or other minor
   descriptions, referenced in the layout section.

#. A ``content`` document that holds the major content of the
   document.

There is no functional difference between ``meta`` and ``content``
fields except that they each provide a distinct namespace for table
content.

``table_builder.py`` generates ``.rst`` output files from ``.yaml``
files. The documents processed by Sphinx use the ``.. include::``
reStructureText directive to include the ``.rst`` file. The build
system includes targets (generated,) for all tables, which are a
dependency of the Sphinx build process. [#table-deps-exception]_

**Use**: To add a table:

- create an appropriate ``.yaml`` file using any of the existing files
  as an example.

- include the generated ``.rst`` file in your Sphinx document. (Optional.)

- in the ``tables`` variable in the ``bin/builder_data.py`` file, add
  a tuple to the list in the following form: ::

       ('$(rst-include)/table-sql-to-agg-terms', 'agg'),

  The first element is the path of the table file, without the
  extension. This value becomes the target in a makefile, so you can
  use the make variables in the string. The second value, ``agg``, in
  the above example is the *block identifer* of the makefile. Ensure that
  related tables have the same block identifier.

.. [#table-deps-exception] To prevent a build error, tables are a
   dependency of all Sphinx builds *except* the ``dirhtml``,
   ``singlehtml``, and ``latex`` builds, which run concurrently during
   the production build process. If you change tables, and run any of
   these targets without building the ``tables`` target, you the table
   will not refresh.

Generated Makefiles
~~~~~~~~~~~~~~~~~~~

System
``````

While the ``makefile`` in the top level of documentation source
coordinates the build process, most of the build targets and build
system exist in the form of makefiles generated by a collection of
Python scripts. This architecture reduces redundancy while increasing
clarity and consistency.

These makefiles enter the build process by way of include statements
and a pattern rule in the top level makefile, as follows: ::

     -include $(output)/makefile.tables
     -include $(output)/makefile.sphinx

     $(output)/makefile.%:bin/makefile-builder/%.py bin/makefile_builder.py bin/builder_data.py
             @$(PYTHONBIN) bin/makefile-builder/$(subst .,,$(suffix $@)).py $@

This will rebuild any of the include files that match the pattern
``$(output)/makefile.%``, if the corresponding python script changes,
*or* it will rebuild all generated makefiles if the
``builder_data.py`` or the ``makefile_builder.py`` files change.

The Python scripts that output these makefiles, all use the
``MakefileBuilder`` class in the ``makefile_builder.py`` file, and are
all located in the ``bin/makefile-builder/`` directory. Consider a
simplified example Python code: :: 

     from makefile_builder import MakefileBuilder
     from builder_data import sphinx

     m = MakefileBuilder()

     m.section_break('sphinx targets', block='sphinx')
     m.comment('each sphinx target invokes and controls the sphinx build.', block='sphinx')
     m.newline(block='sphinx')

     for (builder, prod) in sphinx:
         m.newline(1, builder)
         m.append_var('sphinx-targets', builder)

         if prod is True and builder != 'epub': 
             b = 'production'
             m.target(builder, block=b)
         else:
             b = 'testing'
             m.target(builder, 'sphinx-prerequisites', block=b)

         m.job('mkdir -p $(branch-output)/' + builder, block=b)
         m.msg('[$@]: created $(branch-output)/' + builder, block=b)
         m.msg('[sphinx]: starting $@ build', block=b)
         m.msg('[$@]: build started at `date`.', block=b)
         m.job('$(SPHINXBUILD) -b $@ $(ALLSPHINXOPTS) $(branch-output)/$@', block=b)

     m.write('makefile.output-filename')
     
You can also call ``m.print_content()`` to render the makefile to
standard output. See ``makefile_builder.py`` for the more methods that
you can use to define makefiles. This code will generate a makefile
that resembles the following: ::
 
     sphinx-targets += epub
     epub:sphinx-prerequisites
             @mkdir -p $(branch-output)/epub
             @echo [$@]: created $(branch-output)/epub
             @echo [sphinx]: starting $@ build
             @echo [$@]: build started at `date`.
             @$(SPHINXBUILD) -b $@ $(ALLSPHINXOPTS) $(branch-output)/$@

     sphinx-targets += html
     html:sphinx-prerequisites
             @mkdir -p $(branch-output)/html
             @echo [$@]: created $(branch-output)/html
             @echo [sphinx]: starting $@ build
             @echo [$@]: build started at `date`.
             @$(SPHINXBUILD) -b $@ $(ALLSPHINXOPTS) $(branch-output)/$@

     sphinx-targets += gettext
     gettext:sphinx-prerequisites
             @mkdir -p $(branch-output)/gettext
             @echo [$@]: created $(branch-output)/gettext
             @echo [sphinx]: starting $@ build
             @echo [$@]: build started at `date`.
             @$(SPHINXBUILD) -b $@ $(ALLSPHINXOPTS) $(branch-output)/$@

All information about the targets themselves are in the
``builder_data.py`` file, that contains a number of variables that
hold lists of tuples with information used by the Python scripts to
generate the build rules. Comments explain the structure of the data
in ``builder_data.py``.

System
``````

The build system contains the following 8 makefiles: 

- *pdfs*: Encodes the process for transforming Sphinx's LaTeX output
  into pdfs. 

- *tables*: Describes the process for building all tables generated
  using ``table_builder.py``. 

- *links*: Creates the symbolic links required for production
  builds.

- *sphinx*: Generates the targets for Sphinx. These are mostly, but
  not entirely consistent with the default targets provided by Sphinx
  itself.

- *releases*: Describe targets for generating files for inclusion in
  the installation have the versions of MongoDB automatically baked
  into the their text. 

- *errors*: Special processing of the HTTP error pages.

- *migrations*: Describes the migration process for all non-sphinx
  components of the build. 

- *sphinx-migrations*: Ensures that all sphinx migrations are fresh.

Troubleshooting
```````````````

If you experience an issue with the generated makefiles, the generated
files have comments, and are quite human readable. To add new
generated targets or makefiles, experiment first writing makefiles
themselves, and then write scripts to generate the makefiles. 

Because the generated makefiles, and indeed most of the build process
does not echo commands, use ``make -n`` to determine the actual
oration and sequence used in the build process.
