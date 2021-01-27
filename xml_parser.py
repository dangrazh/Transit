#------------------
# Imports 
#------------------
import sys
import os
import errno
import datetime as dt
import tempfile
import pathlib
import getpass
import re
import enum
from dataclasses import dataclass

from bs4 import BeautifulSoup as bs
from bs4.diagnose import diagnose
import pandas as pd


#------------------
# Classes 
#------------------

@dataclass
class TagAndValue:
    key: str
    value: str

class AttributeUsage(enum.Enum):
    add_to_tag_name = 1
    add_to_tag_value = 2
    add_separate_tag = 3
    ignore = 4

class XmlParser():

    #------------------
    # Standard Functions
    #------------------
    def __init__(self, document_string):
        
        # replace the ? in the XML Prolog as this caused
        # BeautifulSoup to return a completely broken object
        if "?" in document_string:
            document_string = document_string.replace('<?xml version="1.0" encoding="ISO-8859-1"?>', '<xml version="1.0" encoding="ISO-8859-1">')

        # set the basic attributes
        self.doc_str = document_string
        self.soup = bs(document_string, 'xml')
        self.tags = self._get_tags()
        self.top_node = self.soup(self.tags[0])[0]
        self.type = self.soup(self.tags[1])[0].name

        # do some basic checks post parsing
        self.source_no_of_tags = document_string.count("</")
        
        self.soup_no_of_tags = len(self.tags)
        if self.soup_no_of_tags < (0.5 * self.source_no_of_tags):
            raise ValueError(f'BeautifulSoup has recognized {self.soup_no_of_tags} tags whearas raw document contains {self.source_no_of_tags} tags')

    #------------------
    # Public Functions 
    #------------------
    def inspect_document_tree(self, attribute_usage=AttributeUsage.ignore):
        # starting_node = self.tags[0]
        self._traverse_document_tree(self.top_node, attribute_usage)

    def inspect_document_flat(self, attribute_usage=AttributeUsage.ignore):
        # starting_node = self.tags[0]
        # print(f'inspecting tag {starting_node.name} and desendants:')
        self._traverse_document_flat(self.top_node, attribute_usage)


    def get_tags_and_values(self, attribute_usage=AttributeUsage.add_to_tag_name, concat_on_key_error=False):

        doc_cont = {}
        self._process_document(self.top_node, doc_cont, attribute_usage, concat_on_key_error)
        return doc_cont

    #------------------
    # Internal Functions
    #------------------
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
                        print(f'{level}{spacing}{bs_elem.name} ({bs_elem.attrs}) -> {bs_elem.string}')
                    else:
                        print(f'{level}{spacing}{bs_elem.name} -> {bs_elem.string}')
                else:
                    print(f'{level}{spacing}{bs_elem.name}')
                
                for child in bs_elem.children:
                    self._traverse_document_tree(child, attribute_usage, level)

    def _traverse_document_flat(self, bs_elem, attribute_usage, path='', level=0):

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
                        print(f'{path}.{bs_elem.name} ({bs_elem.attrs}) -> {bs_elem.string}')
                    else:
                        print(f'{path}.{bs_elem.name} -> {bs_elem.string}')
                else:
                    if len(path) > 0:
                        path = path + '.' + bs_elem.name
                    else:
                        path = bs_elem.name
                
                for child in bs_elem.children:
                    self._traverse_document_flat(child, attribute_usage, path, level)
    
    def _process_document(self, bs_elem, doc_cont, attribute_usage, concat_on_key_error, path=''):

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
                                self._process_field(doc_cont, key, value, concat_on_key_error)
                        else:
                            key = attrs.key
                            value = attrs.value
                            self._process_field(doc_cont, key, value, concat_on_key_error)
                    else:
                        key = f'{path}.{bs_elem.name}'
                        value = bs_elem.string
                        self._process_field(doc_cont, key, value, concat_on_key_error)
                    
                else:
                    if len(path) > 0:
                        path = path + '.' + bs_elem.name
                    else:
                        path = bs_elem.name
                
                for child in bs_elem.children:
                    self._process_document(child, doc_cont, attribute_usage, concat_on_key_error, path)

    def _process_attrs(self, bs_elem, path, attribute_usage):
        attribs = ''
        key = ''
        value = ''
        list_out = []
        ret_val = None

        if attribute_usage == AttributeUsage.add_to_tag_name:
            for item in bs_elem.attrs:
                attribs = attribs + '-' + bs_elem.attrs[item]
            key = f'{path}.{bs_elem.name}{attribs}'
            value = bs_elem.string
            ret_val = TagAndValue(key=key, value=value)

        elif attribute_usage == AttributeUsage.add_to_tag_value:
            for item in bs_elem.attrs:
                attribs = attribs + bs_elem.attrs[item] + '-'
            key = f'{path}.{bs_elem.name}'
            value = f'{attribs}{bs_elem.string}'
            ret_val = TagAndValue(key=key, value=value)

        elif attribute_usage == AttributeUsage.add_separate_tag:
            for item in bs_elem.attrs:
                # build a list of tags and values for each attribute
                key = f'{path}.{bs_elem.name}.{item}'
                value = bs_elem.attrs[item]
                list_out.append(TagAndValue(key=key, value=value))
            # and finally the tags value
            key = f'{path}.{bs_elem.name}.{bs_elem.name}'
            value = bs_elem.string
            list_out.append(TagAndValue(key=key, value=value))
            ret_val = list_out

        elif attribute_usage == AttributeUsage.ignore:
            key = f'{path}.{bs_elem.name}'
            value = bs_elem.string
            ret_val = TagAndValue(key=key, value=value)

        return ret_val
    
    def _process_field(self, doc_cont, key, value, concat_on_key_error):

        if key in doc_cont:
            if concat_on_key_error:
                old_value = doc_cont[key]
                doc_cont[key] = old_value + " | " + value
            else:
                raise KeyError(f'Trying to append the tag {key} which already exists in document! '
                                f'Current tag value: {value} '
                                f'Existing tag value: {doc_cont[key]}'
                                )
        else:
            doc_cont[key] = value


class FileProcessor():

    #------------------
    # Standard Functions
    #------------------

    def __init__(self, file_handle):
        
        # basic attributes
        self.file_handle = file_handle
        self.file_full_name = file_handle.name
        self.file_path = os.path.abspath(file_handle.name)
        self.file_name = os.path.basename(file_handle.name)
        self.file_name_root = os.path.splitext(self.file_name)[0]

        # get the current temporary directory
        self.temp_path = tempfile.gettempdir()

        # define the identifiers of a xml document
        self.xml_identifiers = {}
        comp_re_xml_prolog = re.compile(r'(<\?xml version=\".*?\" encoding=\".*?\"\?>)')
        self.xml_identifiers['xml_prolog'] = comp_re_xml_prolog
        comp_re_xsd= re.compile(r'(<Document .*?xmlns=.*?>)')
        self.xml_identifiers['xsd'] = comp_re_xsd

        # §§§ NOT YET USED - NEEDS TO BE INTEGRATED INTO PROCESS FILE §§§
        # define tags to ignore
        #'<?xml-stylesheet type="text/xsl" href="simple.xsl" ?>'
        self.tags_to_ignore = {'script'}
        # §§§ NOT YET USED - NEEDS TO BE INTEGRATED INTO PROCESS FILE §§§
        
        #read the file into a list of single xml documents 
        self.xml_source = self._split_into_documents()
        self.no_of_docs_in_file = len(self.xml_source)

        # initiate the internal store for the the output
        self.doc_types = {}

    def __str__(self):
        out_string = (
                    f'file_full_name: {self.file_full_name}\n'
                    f'file_path: {self.file_path}\n'
                    f'file_name: {self.file_name}\n'
                    f'file_name_root: {self.file_name_root}\n'
                    f'no_of_docs_in_file: {self.no_of_docs_in_file}\n'
                    f'temp_path: {self.temp_path}\n'
                    )
        return out_string
    
    def __repr__(self):
        return self.__str__()

    #------------------
    # Public Functions 
    #------------------
    def process_file(self, attribute_usage=AttributeUsage.add_separate_tag,  concat_on_key_error=True):

        # process the data
        for index, xml_doc in enumerate(self.xml_source, start=1):
            print(f'START: Processing document #{index}...')
            try:
                xml_parsed = XmlParser(xml_doc)
            except ValueError as e:
                print(f'ERROR: skipping document #{index} due to the following error: {e}')
            else:
                print(f'INFO: document #{index} successfully loaded')

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
                    tags_n_values = xml_parsed.get_tags_and_values(attribute_usage,  concat_on_key_error)
                except KeyError as e:
                    print(f'ERROR: skipping document #{index} due to the following error: {e}')
                else:
                    # append the new record to the list for the current document type
                    # and store/update the new list in the dict holding all document type lists
                    doc_data.append(tags_n_values)
                    self.doc_types[xml_parsed.type] = doc_data


    def to_excel(self):

        # create the output
        cnt_files = 0
        
        user = getpass.getuser()
        dt_now = dt.datetime.now()
        timestamp = dt_now.strftime("%Y%m%d_%H%M%S")

        file_out_path = self.temp_path + '/'
        file_out_name = f'{self.file_name_root}_{user}_{timestamp}.xlsx'
        file_out = file_out_path + file_out_name

        # if we have output to produce, loop through the dict holding all document type lists
        # and create an Excel file for each output type
        if len(self.doc_types) > 0:
            # create the excel writer object
            with pd.ExcelWriter(file_out, engine='xlsxwriter') as writer: # pylint: disable=abstract-class-instantiated
                for item in self.doc_types:
                    df = pd.DataFrame(self.doc_types[item])
                    df.to_excel(writer, index=False, sheet_name=item)
                    cnt_files += 1
            print(f'{cnt_files} data tabs created in output file!')
        else:
            print('No output data extracted - Excel file not created!')



    #------------------
    # Internal Functions
    #------------------
    def _split_into_documents(self):
        list_out = []
        file_content = self.file_handle.read()
        delims = self._get_delimiters(file_content)
        if len(delims) > 1:
            # more than one delimiter dectectd loop and split 
            # as long as there are identifiers left -> 
            # construct the list as we loop through the identifiers
            
            # inital split
            list_out = self._split_keep(file_content, delims[0])
            # subsequent splits
            for delim in delims[1:]:
                for item in list_out:
                    if delim in item:
                        list_tmp = self._split_keep(item, delim)
                        list_out.extend(list_tmp)
                    else:
                        #delim not found -> skip
                        pass
        else:
            list_out = self._split_keep(file_content, delims[0])

        return list_out


    def _split_keep(self, str_in, delimiter):
        split = str_in.split(delimiter)
        return [substr + delimiter for substr in split[:-1]] + [split[-1]]
    
    def _get_delimiters(self, str_in):
        # identify the delimiters for the file -> for that scan
        # the file for XML Prologs and DTD or
        # XSD patterns
        patts = set()
        for key, comp_re in self.xml_identifiers:
            result = comp_re.finditer(str_in)
            if result:
                for match in result:
                    patts.add(match.group(1))

        return list(patts)


#-------------------------------------------------------------------------------
# General Service Functions
#-------------------------------------------------------------------------------

def write_log(message):

    """ 
    Writes the input message to the log file and sends it to the print
    function at the same time.
    """

    dt_now = dt.datetime.now()
    str_now = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    message = str_now + '   ' + message

    #tell it on the console
    print(message)

    #write it to the log

    # get the current temporary directory
    tmpdir = tempfile.gettempdir()

    # Open the log file
    fileoutname = f'{tmpdir}\\WebDownload.log'
    file_out = open(fileoutname, "a+")
    file_out.write(message + '\n')

    # Close opend file
    file_out.close()


def remove_old_log():

    """
    Function to remove any old log file
    """

    # get the current temporary directory
    tmpdir = tempfile.gettempdir()

    # build the log file name
    fileoutname = f'{tmpdir}\\WebDownload.log'

    #now remove it if exists
    silent_remove(fileoutname)


def silent_remove(filename):

    """
    Function to remove a given file if exists
    """


    # try to remove the file
    try:
        os.remove(filename)

    # if there was an error, raise it if its not "the no such file or directory" error
    except OSError as e:
        if e.errno != errno.ENOENT: # errno.ENOENT = no such file or directory
            raise # re-raise exception if a different error occurred

def file_exists(file_path_name):

    """
    Checks if a file exists and returns a boolean value indicating the same
    """

    #check if file exists and return true or false
    my_file = pathlib.Path(file_path_name)
    return bool(my_file.is_file())

#-------------------------------------------------------------------------------
# Specific Service Functions
#-------------------------------------------------------------------------------

# none for now

#-------------------------------------------------------------------------------
# Main Processing
#-------------------------------------------------------------------------------

# not separated from script entry point for now


#-------------------------------------------------------------------------------
# The script entry point
#-------------------------------------------------------------------------------

if __name__ == "__main__":

    path_name = '<here goes the path >'
    # file_name = 'SYSTEM.DEAD.LETTER.QUEUE_single_xml_per_line_V2.txt' 
    file_name = '<here goes the file name>' 
    # file_name = 'SmallSample.txt'
    file_in = path_name + file_name

    with open(file_in) as f_in:
        # load the file into the file processor
        fp = FileProcessor(f_in)

        #get the basic information for the file
        print(fp)
        # parse the file into the 
        fp.process_file
