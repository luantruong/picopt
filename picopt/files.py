"""File utility operations."""
from __future__ import print_function
import os

from . import stats
from . import PROGRAM_NAME
from .settings import Settings

REMOVE_EXT = '.%s-remove' % PROGRAM_NAME


def replace_ext(filename, new_ext):
    """Replace the file extention."""
    filename_base = os.path.splitext(filename)[0]
    new_filename = '{}.{}'.format(filename_base, new_ext)
    return new_filename


def _cleanup_after_optimize_aux(filename, new_filename, old_format,
                                new_format):
    """
    Replace old file with better one or discard new wasteful file.
    """
    bytes_in = 0
    bytes_out = 0
    final_filename = filename
    try:
        filesize_in = os.stat(filename).st_size
        filesize_out = os.stat(new_filename).st_size
        bytes_in = filesize_in
        bytes_out = filesize_in  # overwritten on succes below
        if (filesize_out > 0) and ((filesize_out < filesize_in) or
                                   Settings.bigger):
            if old_format != new_format:
                final_filename = replace_ext(filename,
                                             new_format.lower())
            rem_filename = filename + REMOVE_EXT
            if not Settings.test:
                os.rename(filename, rem_filename)
                os.rename(new_filename, final_filename)
                os.remove(rem_filename)
            else:
                os.remove(new_filename)

            bytes_out = filesize_out  # only on completion
        else:
            os.remove(new_filename)
    except OSError as ex:
        print(ex)

    return final_filename, bytes_in, bytes_out


def cleanup_after_optimize(filename, new_filename, old_format, new_format):
    """
    Replace old file with better one or discard new wasteful file.

    And report results using the stats module.
    """
    final_filename, bytes_in, bytes_out = _cleanup_after_optimize_aux(
        filename, new_filename, old_format, new_format)
    return stats.ReportStats(final_filename, bytes_count=(bytes_in, bytes_out))
