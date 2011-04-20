======================
Contributing to csvkit
======================

Welcome!
========

Thanks for your interest in contributing to csvkit. There is work be done by developers of all skill levels.

Process for contributing code
=============================

Contributors should use the following roadmap to guide them through the process of submitting a contribution:

#. Fork the project on `Github <https://github.com/onyxfish/csvkit>`_.
#. Check out the `issue tracker <https://github.com/onyxfish/csvkit/issues>`_ and find a task that needs to be done and is of a scope you can realistically expect to complete in a few days. Don't worry about the priority of the issues at first, but try to choose something you'll enjoy. You're much more likely to finish something to the point it can be merged if it's something you really enjoy hacking on.
#. Comment on the ticket letting everyone know you're going to be hacking on it so that nobody duplicates your effort. It's also good practice to provide some general idea of how you plan on resolving the issue so that other developers can make suggestions.
#. Write tests for the feature you're building. Follow the format of the existing tests in the test directory to see how this works. You can run all the tests with the command ``nosetests``. The one exception to testing is command-line scripts. These don't need unit test, though all reusable components should be factored into library modules.
#. Write the code. Try to stay consistent with the style and organization of the existing codebase. A good patch won't be refused for stylistic reasons, but large parts of it may be rewritten and nobody wants that. 
#. As your coding, periodically merge in work from the master branch and verify you haven't broken anything by running the test suite.
#. Write documentation for user-facing features (and library features once the API has stabilized).
#. Once it works, is tested, and has documentation, submit a pull request on Github.
#. Wait for it to either be merged or to recieve a comment about what needs to be fixed.
#. Rejoice.

Legalese
========

To the extent that they care, contributors should keep the following legal mumbo-jumbo in mind:

The source of csvkit and therefore of any contributions are licensed under the permissive `MIT license <http://www.opensource.org/licenses/mit-license.php>`_. By submitting a patch or pull request you are agreeing to release your code under this license. You will be acknowledged in the AUTHORS file. As the owner of your specific contributions you retain the right to privately relicense your specific code contributions (and no others), however, the released version of the code can never be retracted or relicensed.

