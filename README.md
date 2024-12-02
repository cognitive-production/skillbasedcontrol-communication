<h1 style="text-align:center;">
<span style="color:#005B7F;">SkillBasedControl (SBC)</span> Client
</h1>

## Description
This python package provides a high level class for communicating with skills implemented in assets with a SkillBasedControlFramework. Currently communication via OPC-UA is implemented. It is used in the skillbasedcontrol framework developed by Fraunhofer Institute for Machine Tools and Forming Technology, department of IIOT-Controls and Technical Cybernetics.

## How to pip install
#### with existing python evnironment:
```
pip install git+https://github.com/cognitive-production/skillbasedcontrol-client
or try
pip install git+https://user:password@github.com/cognitive-production/skillbasedcontrol-client
```
#### with new conda environment:
```
conda create -n sbc-communication python=3.10
conda activate sbc-communication
pip install git+https://github.com/cognitive-production/skillbasedcontrol-client
or try
pip install git+https://user:password@github.com/cognitive-production/skillbasedcontrol-client
```

## Documentation
...

also see [docs](docs):
* [Overview Class Diagram](docs/overview_classdiagram.md)
* imports [skillstatemachine](https://github.com/cognitive-production/skillbasedcontrol-statemachine) package
* TODO: Sequence diagram
* TODO: Usecase diagram


## Release Notes

### [1.0.0](https://gitlab.cc-asp.fraunhofer.de/cpps/skillbasedcontrolframework/python_skillcommunication/compare/0.7.1...1.0.0) (2024-12-02)
> Rename package to sbc_communication!

#### Upgrade Steps
* see "How to pip install"

#### Breaking Changes
* Rename package to sbc_communication!

#### New Features
* None

#### Bug Fixes
* None

#### Performance Improvements
* None

#### Other Changes
* remove endpoint infos from tests

## License
MIT License, see [LICENSE](LICENSE)
