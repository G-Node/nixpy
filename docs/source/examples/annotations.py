import nixio

def main():

    nixfile = nixio.File.open("annotations.nix", mode=nixio.FileMode.Overwrite)
    block = nixfile.create_block("recording 1", "nix.session")
    
    session = nixfile.create_section('recording session', 'odml.recording')
    session['experimenter'] = 'John Doe'
    session['recording date'] = '2014-01-01'
    
    subject = session.create_section('subject', 'odml.subject')
    subject['id'] = 'mouse xyz'

    cell = subject.create_section('cell', 'odml.cell')
    v = -64.5
    p = cell.create_property('resting potential', -64.5)
    p.uncertainty = 2.25
    p.unit = 'mV'

    # set the recording block metadata
    block.metadata = session

    # query the metadata
    block.metadata.pprint(max_depth=-1)

    print(block.metadata["subject"]["cell"]["resting potential"])

    print(session.find_sections(lambda s: s.name.lower() == "cell"))
    
    print(session.find_sections(lambda s: "resting potential" in s.props))
    print(session.find_sections(lambda s: "resting potential" in s.props)[0]["resting potential"])
    nixfile.close()

if __name__ == "__main__":
    main()

