### This is supposed to act as a template for an argument parser for your script.
### It should be copied into the script where it is needed (or a separate script for import) and then edited as appropriate.
### Importing it as-is will probably not be particularly useful.

def run_argparser():
    import argparse

    parser = argparse.ArgumentParser(
        description="""
        This is a description of the function. 
        When you pull up the functional help text with -h, it will tell you all sorts of information about the function.

        You can include lots of things on multiple lines if you want.
        (Maybe there's a manuscript citation here.)
        """
    )
    parser.add_argument(
        "--sample-name",
        help="(Optional) Name of sample being processed.",
        default="cnvloh_sample" #Includes a default parameter here.
    )
    parser.add_argument(
        "--organism",
        help="Organism type, to adjust certain parameters for biological differences (ploidy, sex chromosomes, etc.)",
        choices=["mammal","bird","bee","yeast","bacterium"], #This lets you set a fixed list of options, and if the user selects something not on the list, the script will refuse execution.
        default="mammal"
    )
    parser.add_argument(
        "--genome-info",
        help="Path to file showing chromosome lengths and centromere positions.", #A required parameter. Script will refuse to execute without it.
        required=True
    )
    parser.add_argument(
        "--chr",
        action="append",
        help="(Optional) Chromosome(s) to plot. If not specified, plots all chromosomes." #Can be set more than once, i.e. --chr 1 --chr 2, and will return a list.
    )
    parser.add_argument(
        "input-files",
        nargs="+",
        help="Positional list of input files.", #Will return a list even if only one is given. Must include at least one.
        required=True
    )
    return parser