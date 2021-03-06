#!/usr/bin/python

import sys
from makefile_builder import MakefileBuilder
from builder_data import links as links_to_create

# to add a symlink build process, add a tuple to the ``links`` in the builder definitions file.

m = MakefileBuilder()

def make_all_links(links):
    m.comment('each link is created in the root and then moved into place using the "create-link" script.', block='header')
    m.newline(block='header')

    for link in links:
        make_link(link[0], link[1], link[2])

    m.comment('meta-targets for testing/integration with rest of the build. must apear at the end', block='footer')
    m.newline(block='footer')

    m.target('.PHONY', 'links clean-links $(public-output)/manual', block='footer')
    m.target('links', '$(LINKS)', block='footer')
    m.newline(block='footer')
    m.target('clean-links', block='footer')
    m.job('rm -rf $(LINKS)', True)

def make_link(make_target, link_target, makefile_block):
    if makefile_block == 'content':
        pass
    else:
        m.append_var('LINKS', make_target, makefile_block)

    m.target(make_target, '', makefile_block)
    m.job('@bin/create-link ' + link_target + ' $(notdir $@) $@', makefile_block)
    m.msg('[symlink]: created a link at: $@', makefile_block)
    m.newline(block=makefile_block)

def main():
    make_all_links(links_to_create)

    m.write(sys.argv[1])

    print('[meta-build]: built "' + sys.argv[1] + '" to specify symlink builders.')

if __name__ == '__main__':
    main()
