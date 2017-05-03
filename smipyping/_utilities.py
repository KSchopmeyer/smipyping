"""
Common utility functions used in multiple modules of this package.
"""
__all__ = ['display_argparser_args']


def display_argparser_args(args):
    """
    Display  argparser ouput options list.

    parameters:
      args - Argparser output
    """
    attrs = vars(args)
    print('cli arguments')
    print('\n'.join("%s: %s" % item for item in attrs.items()))
    print('')
