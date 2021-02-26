# ------------------
# Imports
# ------------------
# import sys
import os

# import errno
import datetime as dt
import tempfile

# import pathlib
# import getpass
import re
import enum
from dataclasses import dataclass
import pandas as pd

from bs4 import BeautifulSoup as bs
from bs4.diagnose import diagnose


# ------------------
# Classes
# ------------------


@dataclass
class TagAndValue:
    key: str
    value: str


class AttributeUsage(enum.Enum):
    add_to_tag_name = 1
    add_to_tag_value = 2
    add_separate_tag = 3
    ignore = 4


class XmlParser:

    # ------------------
    # Standard Functions
    # ------------------
    def __init__(self, document_string):

        # replace the ? in the XML Prolog as this caused
        # BeautifulSoup to return a completely broken object
        if "?" in document_string:
            # §§§ TODO: make this an regex §§§
            document_string = document_string.replace(
                '<?xml version="1.0" encoding="ISO-8859-1"?>',
                '<xml version="1.0" encoding="ISO-8859-1">',
            )

        # set the basic attributes
        self.doc_str = document_string
        self.soup = bs(document_string, "xml")
        self.tags = self._get_tags()
        self.top_node = self.soup(self.tags[0])[0]
        # §§§ TODO: make this configurable
        self.type = self.soup(self.tags[1])[0].name

        # do some basic checks post parsing
        self.source_no_of_tags = document_string.count("</")

        self.soup_no_of_tags = len(self.tags)
        if self.soup_no_of_tags < (0.5 * self.source_no_of_tags):
            raise ValueError(
                f"BeautifulSoup has recognized {self.soup_no_of_tags} tags whearas raw document contains {self.source_no_of_tags} tags"
            )

    # ------------------
    # Public Functions
    # ------------------
    def inspect_document_tree(self, attribute_usage=AttributeUsage.ignore):
        # starting_node = self.tags[0]
        self._traverse_document_tree(self.top_node, attribute_usage)

    def inspect_document_flat(self, attribute_usage=AttributeUsage.ignore):
        # starting_node = self.tags[0]
        # print(f'inspecting tag {starting_node.name} and desendants:')
        self._traverse_document_flat(self.top_node, attribute_usage)

    def get_tags_and_values(
        self, attribute_usage=AttributeUsage.add_to_tag_name, concat_on_key_error=False
    ):

        doc_cont = {}
        self._process_document(
            self.top_node, doc_cont, attribute_usage, concat_on_key_error
        )
        return doc_cont

    # ------------------
    # Internal Functions
    # ------------------
    def _get_tags(self):
        soup_tags = []
        for itm in self.soup.descendants:
            if itm.name:
                soup_tags.append(itm.name)

        return soup_tags

    def _traverse_document_tree(self, bs_elem, attribute_usage, level=0):

        level += 1
        spacing = "  " * level

        if str(type(bs_elem)) == "<class 'bs4.element.Tag'>":
            if bs_elem.name:
                if bs_elem.string and len(list(bs_elem.descendants)) == 1:
                    # Tag with value and no further descendants -> we are at the bottom of the tree, print both the tag and the value
                    if bs_elem.attrs:
                        print(
                            f"{level}{spacing}{bs_elem.name} ({bs_elem.attrs}) -> {bs_elem.string}"
                        )
                    else:
                        print(f"{level}{spacing}{bs_elem.name} -> {bs_elem.string}")
                else:
                    print(f"{level}{spacing}{bs_elem.name}")

                for child in bs_elem.children:
                    self._traverse_document_tree(child, attribute_usage, level)

    def _traverse_document_flat(self, bs_elem, attribute_usage, path="", level=0):

        if str(type(bs_elem)) == "<class 'bs4.element.Tag'>":
            if bs_elem.name:
                if bs_elem.string and len(list(bs_elem.descendants)) == 1:
                    # Tag with value and no further descendants -> we are at the bottom of the tree, print both the tag and the value

                    # old version expanding the attributes -> as this is to inspect the document, new version just displays
                    # the attributes as they are in the docuemnt
                    # attribs = ''
                    # if bs_elem.attrs:
                    #     for item in bs_elem.attrs:
                    #         attribs = attribs + '-' + bs_elem.attrs[item]
                    # print(f'{path}.{bs_elem.name}{attribs} -> {bs_elem.string}')

                    if bs_elem.attrs:
                        print(
                            f"{path}.{bs_elem.name} ({bs_elem.attrs}) -> {bs_elem.string}"
                        )
                    else:
                        print(f"{path}.{bs_elem.name} -> {bs_elem.string}")
                else:
                    if len(path) > 0:
                        path = path + "." + bs_elem.name
                    else:
                        path = bs_elem.name

                for child in bs_elem.children:
                    self._traverse_document_flat(child, attribute_usage, path, level)

    def _process_document(
        self, bs_elem, doc_cont, attribute_usage, concat_on_key_error, path=""
    ):

        if str(type(bs_elem)) == "<class 'bs4.element.Tag'>":
            if bs_elem.name:
                if bs_elem.string and len(list(bs_elem.descendants)) == 1:
                    # Tag with value and no further descendants -> we are at the bottom of the tree, print both the tag and the value
                    attrs = None
                    if bs_elem.attrs:
                        attrs = self._process_attrs(bs_elem, path, attribute_usage)
                        if isinstance(attrs, list):
                            # we have a list of attrs to turn into fields
                            for attr in attrs:
                                key = attr.key
                                value = attr.value
                                self._process_field(
                                    doc_cont, key, value, concat_on_key_error
                                )
                        else:
                            key = attrs.key
                            value = attrs.value
                            self._process_field(
                                doc_cont, key, value, concat_on_key_error
                            )
                    else:
                        key = f"{path}.{bs_elem.name}"
                        value = bs_elem.string
                        self._process_field(doc_cont, key, value, concat_on_key_error)

                else:
                    if len(path) > 0:
                        path = path + "." + bs_elem.name
                    else:
                        path = bs_elem.name

                for child in bs_elem.children:
                    self._process_document(
                        child, doc_cont, attribute_usage, concat_on_key_error, path
                    )

    def _process_attrs(self, bs_elem, path, attribute_usage):
        attribs = ""
        key = ""
        value = ""
        list_out = []
        ret_val = None

        if attribute_usage == AttributeUsage.add_to_tag_name:
            for item in bs_elem.attrs:
                attribs = attribs + "-" + bs_elem.attrs[item]
            key = f"{path}.{bs_elem.name}{attribs}"
            value = bs_elem.string
            ret_val = TagAndValue(key=key, value=value)

        elif attribute_usage == AttributeUsage.add_to_tag_value:
            for item in bs_elem.attrs:
                attribs = attribs + bs_elem.attrs[item] + "-"
            key = f"{path}.{bs_elem.name}"
            value = f"{attribs}{bs_elem.string}"
            ret_val = TagAndValue(key=key, value=value)

        elif attribute_usage == AttributeUsage.add_separate_tag:
            for item in bs_elem.attrs:
                # build a list of tags and values for each attribute
                key = f"{path}.{bs_elem.name}.{item}"
                value = bs_elem.attrs[item]
                list_out.append(TagAndValue(key=key, value=value))
            # and finally the tags value
            key = f"{path}.{bs_elem.name}.{bs_elem.name}"
            value = bs_elem.string
            list_out.append(TagAndValue(key=key, value=value))
            ret_val = list_out

        elif attribute_usage == AttributeUsage.ignore:
            key = f"{path}.{bs_elem.name}"
            value = bs_elem.string
            ret_val = TagAndValue(key=key, value=value)

        return ret_val

    def _process_field(self, doc_cont, key, value, concat_on_key_error):

        if key in doc_cont:
            if concat_on_key_error:
                old_value = doc_cont[key]
                doc_cont[key] = old_value + " | " + value
            else:
                raise KeyError(
                    f"Trying to append the tag {key} which already exists in document! "
                    f"Current tag value: {value} "
                    f"Existing tag value: {doc_cont[key]}"
                )
        else:
            doc_cont[key] = value


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
        comp_re_xml_prolog = re.compile(r"(<\?xml version=\".*?\" encoding=\".*?\"\?>)")
        self.xml_identifiers["xml_prolog"] = comp_re_xml_prolog
        comp_re_xsd = re.compile(r"(<Document .*?xmlns=.*?>)")
        self.xml_identifiers["xsd"] = comp_re_xsd

        # define tags to ignore
        self.tags_to_ignore = {"script"}
        # §§§ TODO: - NEEDS TO BE INTEGRATED INTO PROCESS FILE §§§

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

        # process the data
        for index, xml_doc in enumerate(self.xml_source, start=1):
            print(f"START: Processing document #{index}...")
            try:
                xml_parsed = XmlParser(xml_doc)
            except ValueError as e:
                print(
                    f"ERROR: skipping document #{index} due to the following error: {e}"
                )
            else:
                print(f"INFO: document #{index} successfully loaded")

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
                    print(
                        f"ERROR: skipping document #{index} due to the following error: {e}"
                    )
                else:
                    # append the new record to the list for the current document type
                    # and store/update the new list in the dict holding all document type lists
                    doc_data.append(tags_n_values)
                    self.doc_types[xml_parsed.type] = doc_data

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

    def to_excel(self, out_path=None):
        # create the output
        cnt_files = 0

        # user = getpass.getuser()
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
        list_out_tmp = []
        list_out = []
        delims = self._get_delimiters(self.file_content)
        if len(delims) > 1:
            # more than one delimiter dectectd loop and split
            # as long as there are identifiers left ->
            # construct the list as we loop through the identifiers
            print(f"delims found: {delims}")

            # inital split
            list_out = self._split_keep(self.file_content, delims[0])
            # subsequent splits
            for delim in delims[1:]:
                for item in list_out:
                    if delim in item:
                        list_tmp = self._split_keep(item, delim)
                        list_out_tmp.extend(list_tmp)
                    else:
                        # delim not found -> skip
                        pass
        else:
            list_out_tmp = self._split_keep(self.file_content, delims[0])

        # by now we have a list that has the delimiter followed by the actual
        # content as a pair - we need to bring them togehter again - at the same
        # occation we remove any newline that might be in the document, so that's
        # what comes here
        msg = ""
        it = iter(list_out_tmp)
        for x, y in zip(it, it):
            msg = f"{x}{y}"
            msg = msg.replace("\n", "")
            list_out.append(msg)

        return list_out

    def _split_keep(self, str_in, delimiter):
        split = str_in.split(delimiter)
        return [substr + delimiter for substr in split[:-1]] + [split[-1]]

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
    file_name = "camt.054_sweden.xml"
    # file_name = "pain.008.sepa.xml"
    file_in = path_name + file_name

    # with open(file_in) as f_in:
    # load the file into the file processor
    fp = FileProcessor(file_in)

    # get the basic information for the file
    print(f"FileProcessor object:\n{fp}")

    # parse the documents within the file
    # this is where the actual XML processing happens
    fp.process_file()

    # get the samples - this returns a dict with
    # the 1st document of each document tpye in the file
    print(f"Inspect Sample:\n{fp.inspect_samples()}")

    # export the parsed documents to the excel file
    # fp.to_excel()
