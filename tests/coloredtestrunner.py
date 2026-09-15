# -*- coding: utf-8 -*-
"""
A ColoredTestRunner for use with the Python unit testing framework. It
generates a tabular report to show the result at a glance, with COLORS.

coloredtestrunner.py was modified from code written by Vinícius Dantas and posted
as a gist: https://gist.github.com/viniciusd/73e6eccd39dea5e714b1464e3c47e067
and demonstrated here:
https://stackoverflow.com/questions/17162682/display-python-unittest-results-in-nice-tabular-form/31665827#31665827

The code linked above is based on HTMLTestRunner <http://tungwaiyip.info/software/HTMLTestRunner.html>
written by Wai Yip Tung. The BSD-3-Clause license covering HTMLTestRunner is below.

------------------------------------------------------------------------
Copyright (c) 2004-2007, Wai Yip Tung
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
  this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.
* Neither the name Wai Yip Tung nor the names of its contributors may be
  used to endorse or promote products derived from this software without
  specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import sys
import re
import unittest
import textwrap


# ------------------------------------------------------------------------
# The redirectors below are used to capture output during testing. Output
# sent to sys.stdout and sys.stderr are automatically captured. However
# in some cases sys.stdout is already cached before HTMLTestRunner is
# invoked (e.g. calling logging.basicConfig). In order to capture those
# output, use the redirectors for the cached stream.
#
# e.g.
#   >>> logging.basicConfig(stream=HTMLTestRunner.stdout_redirector)
#   >>>

class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


class Table(object):

    def __init__(self, padding='', allow_newlines=False):
        self.__columnSize__ = []
        self.__rows__ = []
        self.__titles__ = None
        self.padding = padding
        self.allow_newlines = allow_newlines

    def __len__(self, x):
        return len(re.sub(r"\033\[[0-9];[0-9];[0-9]{1,2}m", "", x))

    def addRow(self, row):
        rows = [[''] for i in range(len(row))]
        maxrows = 0
        for i, x in enumerate(row):
            for j, y in enumerate(x.split("\n")):
                if len(y) == 0 and not self.allow_newlines:
                    continue
                try:
                    self.__columnSize__[i] = max(self.__columnSize__[i], self.__len__(y))
                except IndexError:
                    self.__columnSize__.append(self.__len__(y))
                rows[i].append(y)
                maxrows = max(j, maxrows)
        for i in range(len(rows)):
            rows[i] += (maxrows-len(rows[i])+2)*['']
        for i in range(maxrows + 1):
            self.__rows__.append([rows[j][i+1] for j in range(len(row))])

    def addTitles(self, titles):
        for i, x in enumerate(titles):
            try:
                self.__columnSize__[i] = max(self.__columnSize__[i], self.__len__(x))
            except IndexError:
                self.__columnSize__.append(self.__len__(x))
        self.__titles__ = titles

    def __repr__(self):
        hline = self.padding+"+"
        for x in self.__columnSize__:
            hline += (x+2)*'-'+'+'
        rows = []
        if self.__titles__ is None:
            title = ""
        else:
            if len(self.__titles__) < len(self.__columnSize__):
                self.__titles__ += ((len(self.__columnSize__)-len(self.__titles__))*[''])
            for i, x in enumerate(self.__titles__):
                self.__titles__[i] = x.center(self.__columnSize__[i])
            title = self.padding+"| "+" | ".join(self.__titles__)+" |\n"+hline+"\n"
        for x in self.__rows__:
            if len(x) < len(self.__columnSize__):
                x += ((len(self.__columnSize__)-len(x))*[''])
            for i, c in enumerate(x):
                x[i] = c.ljust(self.__columnSize__[i])+(len(c)-self.__len__(c)-3)*' '
            rows.append(self.padding+"| "+" | ".join(x)+" |")
        return hline+"\n"+title+"\n".join(rows)+"\n"+hline+"\n"


class bcolors(object):
    FORMAT = {
        'Regular': '0',
        'Bold': '1',
        'Underline': '4',
        'High Intensity': '0',  # +60 on color
        'BoldHighIntensity': '1',  # +60 on color
    }
    START = "\033["
    COLOR = {
        'black': "0;30m",
        'red': "0;31m",
        'green': "0;32m",
        'yellow': "0;33m",
        'blue': "0;34m",
        'purple': "0;35m",
        'cyan': "0;36m",
        'white': "0;37m",
        'end': "0m",
    }

    def __getattr__(self, name):
        def handlerFunction(*args, **kwargs):
            return self.START+self.FORMAT['Regular']+";"+self.COLOR[name.lower()]
        return handlerFunction(name=name)


# ----------------------------------------------------------------------
# Template

class Template_mixin(object):
    bc = bcolors()

    STATUS = {
        0: bc.GREEN+'pass'+bc.END,
        1: bc.PURPLE+'fail'+bc.END,
        2: bc.RED+'error'+bc.END,
    }

    # ------------------------------------------------------------------------
    # Report
    REPORT_TEST_WITH_OUTPUT_TMPL = r"""
   %(desc)s

        %(status)s

        %(script)s

"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_NO_OUTPUT_TMPL = r"""
    %(desc)s
    %(status)s
"""  # variables: (tid, Class, style, desc, status)

    REPORT_TEST_OUTPUT_TMPL = r"""
%(output)s
"""  # variables: (id, output)


class ColoredTestResult(unittest.TextTestResult):

    stdout_redirector = OutputRedirector(sys.stdout)
    stderr_redirector = OutputRedirector(sys.stderr)

    def __init__(self, stream, descriptions, verbosity=1):
        super(ColoredTestResult, self).__init__(stream, descriptions, verbosity)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.skip_count = 0
        self.verbosity = verbosity

        # deny TextTestResult showAll functionality
        self.showAll = False

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []

    def startTest(self, test):
        super(ColoredTestResult, self).startTest(test)
        # just one buffer for both stdout and stderr
        self.outputBuffer = StringIO()
        self.stdout_redirector.fp = self.outputBuffer
        self.stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector

    def complete_output(self):
        """
        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    def addSuccess(self, test):
        self.success_count += 1
        super(ColoredTestResult, self).addSuccess(test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stdout.write('.')
            sys.stdout.flush()

        if not hasattr(self, 'successes'):
            self.successes = [test]
        else:
            self.successes.append(test)

    def addError(self, test, err):
        self.error_count += 1
        super(ColoredTestResult, self).addError(test, err)
        output = self.complete_output()
        _, _exc_str = self.errors[-1]
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stdout.write('E')
            sys.stdout.flush()

    def addFailure(self, test, err):
        self.failure_count += 1
        super(ColoredTestResult, self).addFailure(test, err)
        output = self.complete_output()
        _, _exc_str = self.failures[-1]
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stdout.write('F')
            sys.stdout.flush()

    def addSubTest(self, test, subtest, err):
        if err is not None:
            if issubclass(err[0], test.failureException):
                self.addFailure(subtest, err)
            else:
                self.addError(subtest, err)

    def addSkip(self, test, reason):
        self.skip_count += 1
        super(ColoredTestResult, self).addSkip(test, reason)
        self.complete_output()
        if self.verbosity > 1:
            sys.stdout.write('s')
            sys.stdout.flush()

    def get_all_cases_run(self):
        '''Return a list of each test case which failed or succeeded
        '''
        cases = []
        if hasattr(self, 'successes'):
            cases.extend(self.successes)
        cases.extend([failure[0] for failure in self.failures])
        return cases


class ColoredTestRunner(Template_mixin):

    def __init__(self, stream=sys.stdout, verbosity=1, title=None, description=None):
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = ''
        else:
            self.title = title
        if description is None:
            self.description = ''
        else:
            self.description = description

        self.startTime = datetime.datetime.now()
        self.bc = bcolors()
        self.desc_width = 40
        self.output_width = 60

    def run(self, test):
        "Run the given test case or test suite."
        result = ColoredTestResult(stream=self.stream, descriptions=True, verbosity=self.verbosity)
        test(result)
        self.stopTime = datetime.datetime.now()
        self.generateReport(test, result)
        return result

    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}
        classes = []
        for n, test, output, error in result_list:
            testClass = test.__class__
            if testClass not in rmap:
                rmap[testClass] = []
                classes.append(testClass)
            rmap[testClass].append((n, test, output, error))
        r = [(testClass, rmap[testClass]) for testClass in classes]
        return r

    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)
        status = []
        padding = 4 * ' '
        if result.success_count:
            status.append(padding + self.bc.GREEN + 'Pass:' + self.bc.END + ' %s\n' % result.success_count)
        if result.failure_count:
            status.append(padding + self.bc.PURPLE + 'Failure:' + self.bc.END + ' %s\n' % result.failure_count)
        if result.error_count:
            status.append(padding + self.bc.RED + 'Error:' + self.bc.END + ' %s\n' % result.error_count)
        if status:
            status = '\n'+''.join(status)
        else:
            status = 'none'
        return [
            ('Start Time', startTime),
            ('Duration', duration),
            ('Status', status),
        ]

    def generateReport(self, test, result):
        report_attrs = self.getReportAttributes(result)
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result)
        output = "\n" + self.title.rjust(30) + "\n" + heading + report
        try:
            self.stream.write(output.encode('utf8'))
        except TypeError:
            self.stream.write(output)

    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.bc.CYAN + name + ": " + self.bc.END + value + "\n"
        a_lines.append(line)
        heading = ''.join(a_lines) + self.bc.CYAN + "Description:" + self.bc.END + self.description + "\n"
        return heading

    def _generate_report(self, result):
        sortedResult = self.sortResult(result.result)
        padding = 4 * ' '
        table = Table(padding=padding, allow_newlines=True)
        table.addTitles(["Test group/Test case", "Count", "Pass", "Fail", "Error"])
        tests = ''
        for cid, (testClass, classResults) in enumerate(sortedResult):  # Iterate over the test cases
            classTable = Table(padding=2*padding)
            classTable.addTitles(["Test name", "Output", "Status"])
            # subtotal for a class
            np = nf = ne = 0
            for n, test, output, error in classResults:
                if n == 0:
                    np += 1
                elif n == 1:
                    nf += 1
                else:
                    ne += 1

            # format class description
            if testClass.__module__ == "__main__":
                name = testClass.__name__
            else:
                name = "%s.%s" % (testClass.__module__, testClass.__name__)
            tests += padding + name + "\n"
            doc = testClass.__doc__ and testClass.__doc__.split("\n")[0] or ""
            if doc:
                doc = self._indent(self._wrap_text(doc, width=self.output_width - 4), 4)
            desc = doc and ('%s:\n%s' % (name, doc)) or name

            table.addRow([self._wrap_text(desc, width=self.desc_width), str(np + nf + ne), str(np), str(nf), str(ne)])
            for tid, (n, test, output, error) in enumerate(classResults):  # Iterate over the unit tests
                classTable.addRow(self._generate_report_test(cid, tid, n, test, output, error))
            tests += str(classTable)

            for tid, (n, test, output, error) in enumerate(classResults):  # Iterate over the unit tests
                if error:
                    tests += self._indent(self.bc.RED + "ERROR in test %s:" % test + self.bc.END, 2)
                    tests += "\n" + self._indent(error, 2) + "\n"

        table.addRow([self.desc_width * '-', '----', '----', '----', '----'])
        table.addRow(["Total", str(result.success_count + result.failure_count + result.error_count),
                      str(result.success_count), str(result.failure_count), str(result.error_count)])
        report = self.bc.CYAN + "Summary: " + self.bc.END + "\n" + str(table) + tests
        return report

    def _generate_report_test(self, cid, tid, n, test, output, error):
        name = test.id().split('.')[-1]
        doc = test.shortDescription() or ""
        if doc:
            doc = self._indent(self._wrap_text(doc, width=self.output_width - 4), 4)
        desc = doc and ('%s:\n%s' % (name, doc)) or name

        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(output, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            try:
                uo = output.decode('latin-1')
            except AttributeError:
                uo = output
        else:
            uo = output
        if isinstance(error, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            try:
                ue = error.decode('latin-1')
            except AttributeError:
                ue = error
        else:
            ue = error

        # just print the last line of any error
        if "\n" in ue:
            ue = ue.splitlines()[-1]

        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            output=self._wrap_text(uo, width=self.output_width) + self._wrap_text(ue, width=self.output_width),
        )
        row = [desc, script, self.STATUS[n]]
        return row

    @staticmethod
    def _wrap_text(text, width):
        """Wrap text to a given width but preserve line breaks
        """
        # https://stackoverflow.com/a/26538082
        return '\n'.join(['\n'.join(textwrap.wrap(line, width, break_long_words=False, replace_whitespace=False))
                          for line in text.splitlines() if line.strip() != ''])

    @staticmethod
    def _indent(text, amount):
        """Indent text by a particular number of spaces on each line
        """
        try:
            return textwrap.indent(text, amount * ' ')
        except AttributeError:  # undefined function (indent wasn't added until Python 3.3)
            return ''.join((amount * ' ') + line for line in text.splitlines(True))
