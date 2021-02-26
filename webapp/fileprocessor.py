# ------------------
# Imports
# ------------------
import os
import datetime as dt
import tempfile
import re

import pandas as pd

# import for usage in flask app
from webapp.xmlparser import XmlParser, AttributeUsage

# import for standalone usage
# from xmlparser import XmlParser, AttributeUsage


class FileProcessor:

    # ------------------
    # Standard Functions
    # ------------------

    def __init__(self, source_file):

        with open(source_file) as file_handle:

            # basic attributes
            # self.file_handle = file_handle
            self.file_content = file_handle.read()
            self.file_full_name = file_handle.name
            self.file_path = os.path.abspath(file_handle.name)
            self.file_name = os.path.basename(file_handle.name)
            self.file_name_root = os.path.splitext(self.file_name)[0]
            self.line_count = self.file_content.count("\n")

        # get the current temporary directory
        self.temp_path = tempfile.gettempdir()

        # define the identifiers of a xml document
        self.xml_identifiers = {}
        # comp_re_xml_prolog = re.compile(r"(<\?xml version=\".*?\" encoding=\".*?\"\?>)")
        comp_re_xml_prolog = re.compile(r"(<\?xml .*?>)")
        self.xml_identifiers["xml_prolog"] = comp_re_xml_prolog
        # comp_re_xsd = re.compile(r"(<Document .*?xmlns=.*?>)")
        comp_re_xsd = re.compile(r"(<Document .*?>)")
        self.xml_identifiers["xsd"] = comp_re_xsd

        # the delimiters and process log stores
        self.doc_delimiters = []
        self.process_log = []

        # flag if file has already been processed
        self.file_processed = False

        # define comments to ignore
        comment_str_open = "<!--"
        comment_str_close = "-->"
        # TODO: include in process file, resp. in pre-processing cleanup

        # define tags to ignore
        self.tags_to_ignore = {"script"}
        # TODO: include in process file, resp. in pre-processing cleanup

        # read the file into a list of single xml documents
        self.xml_source = self._split_into_documents()
        self.no_of_docs_in_file = len(self.xml_source)

        # initiate the internal store for the the output
        self.doc_types = {}

    def __str__(self):
        out_string = (
            f"file_full_name: {self.file_full_name}\n"
            f"file_path: {self.file_path}\n"
            f"file_name: {self.file_name}\n"
            f"file_name_root: {self.file_name_root}\n"
            f"no_of_docs_in_file: {self.no_of_docs_in_file}\n"
            f"temp_path: {self.temp_path}\n"
        )
        return out_string

    def __repr__(self):
        return self.__str__()

    # ------------------
    # Public Functions
    # ------------------
    def process_file(
        self, attribute_usage=AttributeUsage.add_separate_tag, concat_on_key_error=True
    ):

        # initialize the internal store for the the output
        self.doc_types = {}
        self.process_log = []

        # initialize the return value
        out = "success"

        # process the data
        for index, xml_doc in enumerate(self.xml_source, start=1):
            # print(f"START: Processing document #{index}...")
            try:
                xml_parsed = XmlParser(xml_doc)
            except ValueError as e:
                # pass
                # print(
                #     f"ERROR: skipping document #{index} due to the following error: {e}"
                # )
                self.process_log.append(
                    f"ERROR: skipping document #{index} due to the following error: {e}"
                )
                out = "error"
            else:
                # print(f"INFO: document #{index} successfully loaded")
                self.process_log.append(f"INFO: document #{index} successfully loaded")
                # check the document type and either get the list of records
                # if already existing or create a new list if new document type
                if xml_parsed.type in self.doc_types:
                    doc_data = self.doc_types[xml_parsed.type]
                else:
                    doc_data = []
                # read the tags and values from the parsed xml document
                # the error handling is actually not needed as the option
                # concat_on_key_error=True will not raise any KeyErrors
                try:
                    tags_n_values = xml_parsed.get_tags_and_values(
                        attribute_usage, concat_on_key_error
                    )
                except KeyError as e:
                    # print(
                    #     f"ERROR: skipping document #{index} due to the following error: {e}"
                    # )
                    self.process_log.append(
                        f"ERROR: skipping document #{index} due to the following error: {e}"
                    )
                    out = "error"
                else:
                    # append the new record to the list for the current document type
                    # and store/update the new list in the dict holding all document type lists
                    doc_data.append(tags_n_values)
                    self.doc_types[xml_parsed.type] = doc_data

        self.file_processed = True
        return out

    def inspect_samples(self):
        # create the empty dict holding the output
        doc_type_samples = {}

        # loop through the full store of document types and data
        # and return the 1st data element of each as a sample
        for type in self.doc_types:
            doc_type_samples[type] = self.doc_types[type][0]

        return doc_type_samples

    def info(self):
        out = [
            f"File name: {self.file_name_root}",
            f"No of lines in file: {self.line_count}",
            f"No of documents in file: {self.no_of_docs_in_file}",
        ]
        return out

    def debug_info(self):
        out = {
            "No of documents in file": self.no_of_docs_in_file,
            "Tags to ignore": self.tags_to_ignore,
            "Document delimiters found": self.doc_delimiters,
            # "Documents in file": self.xml_source,
            # "Parsed file content": self.doc_types,
        }

        return out

    def to_excel(self, out_path=None):
        # create the output
        cnt_files = 0

        dt_now = dt.datetime.now()
        timestamp = dt_now.strftime("%Y%m%d_%H%M%S")

        if out_path:
            file_out_path = out_path + "/"
        else:
            file_out_path = self.temp_path + "/"

        file_out_name = f"{self.file_name_root}_{timestamp}.xlsx"
        file_out = file_out_path + file_out_name

        # if we have output to produce, loop through the dict holding all document type lists
        # and create an Excel file for each output type
        if len(self.doc_types) > 0:
            # create the excel writer object
            with pd.ExcelWriter(
                file_out, engine="xlsxwriter"
            ) as writer:  # pylint: disable=abstract-class-instantiated
                for item in self.doc_types:
                    df = pd.DataFrame(self.doc_types[item])
                    df.to_excel(writer, index=False, sheet_name=item)
                    cnt_files += 1
            # return f"{cnt_files} data tabs created in output file!"
            return file_out_name
        else:
            return "No output data extracted - Excel file not created!"

    # ------------------
    # Internal Functions
    # ------------------
    def _split_into_documents(self):
        list_out = []
        esc_delims = []
        delims = self._get_delimiters(self.file_content)
        self.doc_delimiters = delims
        if len(delims) > 0:
            # at least one delimiter detected, split the document

            # first escape the found delimiters
            for delim in delims:
                esc_delims.append(re.escape(delim))

            # second split using a positive lookahead (?=...) regex, where (?={}) will be replaced
            # with the escaped delimiters produced above, joined with | to get an "or" match
            # in the regex split function. The (?!$) matches only a location that is not
            # immediately followed with the end of string
            list_raw = re.split(
                r"(?={})(?!$)".format("|".join(esc_delims)), self.file_content
            )
            for item in list_raw:
                if len(item) == 0:
                    pass
                else:
                    list_out.append(item.strip())

        return list_out

    def _get_delimiters(self, str_in):
        # identify the delimiters for the file -> for that scan
        # the file for XML Prologs and DTD or
        # XSD patterns
        patts = set()
        for key in self.xml_identifiers:
            result = self.xml_identifiers[key].finditer(str_in)
            if result:
                for match in result:
                    patts.add(match.group(1))

        return list(patts)


# -------------------------------------------------------------------------------
# General Service Functions
# -------------------------------------------------------------------------------


# -------------------------------------------------------------------------------
# The script entry point
# -------------------------------------------------------------------------------

if __name__ == "__main__":

    path_name = "P:\\Programming\\Python\\xml_examples\\"
    file_name = "mixed.pain.camt.xml"
    # file_name = "camt.054_sweden.xml"
    # file_name = "pain.008.sepa.xml"
    file_in = path_name + file_name

    # with open(file_in) as f_in:
    # load the file into the file processor
    fp = FileProcessor(file_in)

    # get the basic information for the file
    print(f"FileProcessor object:\n{fp}")

    # get the full debug information
    print(fp.debug_info())

    # parse the documents within the file
    # this is where the actual XML processing happens
    fp.process_file()

    # get the samples - this returns a dict with
    # the 1st document of each document tpye in the file
    print(f"Inspect Sample:\n{fp.inspect_samples()}")

    # export the parsed documents to the excel file
    # fp.to_excel()
