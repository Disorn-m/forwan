import os
from typing import Tuple
import string
import itertools
import streamlit as st
from zipfile import ZipFile

def main():

    st.set_page_config(
        layout='wide',
        page_title='Solar PV Far-shading Batch Pre-processing',
        initial_sidebar_state='expanded',
    )

    if "progress_val" not in st.session_state:
        st.session_state.progress_val = 0

    st.write('# Solar PV Far-shading Batch Pre-processing')

    with st.form('form'):

        col1, col2, col3 = st.columns(3)
        vc_file_uploaded = col1.file_uploader(label='**VC File**',
                                              help="Upload the template PVsyst variant (.VC) file for the project.")
        hor_files_uploader = col2.file_uploader(label='**HOR Files** (Allows multiple files)',
                                                help="Upload all horizon (HOR) files to be added into the variant file",
                                                accept_multiple_files=True)
        project_name = col3.text_input(label='**Project name**',
                                       help="Warning: This will overwrite any previous project files with identical name.")

        submit_button = col2.form_submit_button(
            'Run pre-processor', type='primary')

    if submit_button:

        st.write('---')
        st.progress(st.session_state.progress_val)

        vc_file = vc_file_uploaded.getvalue().decode()
        hor_files = [hor_file.getvalue().decode()
                     for hor_file in hor_files_uploader]
        st.session_state.progress_val = 10

        output_files = run(project_name, hor_files, vc_file)
        st.session_state.progress_val = 90
        zipfile = zip_output_files(project_name, output_files)
        st.session_state.progress_val = 100

        if zipfile:
            col1, col2, col3 = st.columns(3)

            col2.success("Files successfully pre-processed")

            with open(f"{project_name}.zip", "rb") as fp:
                btn = col2.download_button(
                    label="Download ZIP",
                    data=fp,
                    file_name=f"{project_name}.zip",
                    mime="application/zip",
                )
            # Clean-up repository
            output_files.append(zipfile)
        remove_files(output_files)


def create_vc_names() -> list[str]:
    vc_prefix = ['VC', 'VD']
    vc_alphabet = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'] + \
        list(string.ascii_uppercase)  # last bit returns all letters of the alphabet

    vc_names = []
    for permutation in itertools.product(vc_prefix, vc_alphabet):
        vc_names.append(permutation[0] + permutation[1])

    return vc_names.__iter__()  # Returns list's iterator to avoid having a file counter


def parse_hor_files(hor_f) -> Tuple:
    point_counter = 0
    # As we can concat strings in a similar way as lists, no need to make this a list.
    comment_line = ''
    point_list = ''

    # Convert bytes to string for parsing
    lines = hor_f.split('\n')
    for line in lines:
        if 'lat' in line or 'lng' in line:
            # Adding spaces to align comment with VC tabbing structure
            comment_line = f'    Comment={line} \n'
        elif '\t' in line:
            angle, horizon = line.split('\t')
            # Horizon contains '\n' at its end, no need to re-add it
            # Adding spaces as above.
            point_list += f'      Point_{point_counter}={angle}, {horizon} \n'
            point_counter += 1
        else:
            break

    # Reconvert to bytes due to file type.
    return comment_line, point_list


def find_section(vc_file: str, header_delimiter: str, tail_delimiter: str) -> str:
    try:
        header_section = vc_file.split(header_delimiter)[0]
        header_section += f'{header_delimiter} \n'
    except Exception:
        raise Exception(
            f'Could not find header end point {header_delimiter}. Check the delimiter exists in file.')

    try:
        tail_section = f'{tail_delimiter}'
        tail_section += vc_file.split(tail_delimiter)[1]
    except Exception:
        raise Exception(
            f'Could not find tail starting point {tail_delimiter}. Check the delimiter exists in file.')

    return header_section, tail_section


def run(project_name, hor_files, vc_file):

    output_files = []
    hor_parsed_files = []

    vc_names = create_vc_names()
    st.session_state.progress_val = 20

    # Prep horizon files
    for hor_file in hor_files:
        hor_parsed_files.append(parse_hor_files(hor_file))

    st.session_state.progress_val = 30

    # Comment insert section
    comment_header, comment_tail = find_section(
        vc_file,
        header_delimiter="  PVObject_Horizon=pvHorizon",
        tail_delimiter="    Flags=$0003"  # Add the correct amount of spaces
    )

    # Point insert section
    point_header, point_tail = find_section(
        comment_tail,  # Using the end section of the above for parser continuity
        header_delimiter="      Mode=1",
        tail_delimiter="  End of PVObject pvHorizon"
    )

    # There are multiple 'End of TCubicProfile' in the file, so looked for next section header.
    # Re-adding previous section header
    point_tail = '      End of TCubicProfile\r\n ' + point_tail

    st.session_state.progress_val = 40

    for hor_comment, hor_points in hor_parsed_files:

        # Create variant name
        variant_name = f'{project_name}.{next(vc_names)}'
        print(f'Creating "{variant_name}" file.')

        # Save file
        with open(f'{variant_name}', "w", encoding='utf-8') as output_file:
            # Concatenate all sections together
            updated_VC = comment_header + hor_comment + \
                point_header + hor_points + point_tail

            # Save file
            output_file.write(updated_VC)
            output_files.append(variant_name)

    return output_files


def zip_output_files(project_name: str, output_files: list[str]):

    zipObj = ZipFile(f"{project_name}.zip", "w")
    for vc_file in output_files:
        zipObj.write(vc_file)
    zipObj.close()

    ZipfileDotZip = f"{project_name}.zip"

    return ZipfileDotZip


def remove_files(files_to_remove: list[str]):
    for f in files_to_remove:
        os.remove(f)


if __name__ == "__main__":
    main()
