# -----------------------------------------------------------------------------.
# MIT License

# Copyright (c) 2024 pycolorbar developers
#
# This file is part of pycolorbar.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# -----------------------------------------------------------------------------.
"""Define the register of univiariate colormaps."""

import os
import tempfile

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from pycolorbar.settings.colormap_io import read_cmap_dict, write_cmap_dict
from pycolorbar.settings.utils import get_auxiliary_categories
from pycolorbar.utils.yaml import list_yaml_files

# Matplotlib Registry Initialization:
# - In the __init__ : from matplotlib.cm import _colormaps as colormaps
# - Instead of singleton pattern, uses globals().updates() for module-level instance
#   --> https://github.com/matplotlib/matplotlib/blob/v3.8.2/lib/matplotlib/cm.py#L59
#   --> https://github.com/matplotlib/matplotlib/blob/v3.8.2/lib/matplotlib/cm.py#L236
#
#   _colormaps = ColormapRegistry()
#   globals().update(_colormaps)


class ColormapRegistry:
    """
    A singleton class to manage colormap registrations.

    This class provides methods to register colormaps, remove them, retrieve colormap file paths,
    and add new colormaps to a temporary directory for further processing.

    Attributes
    ----------
    _instance : ColormapRegistry
        The singleton instance of the ColormapRegistry.
    registry : dict
        The dictionary holding the registered colormap names and their corresponding configuration YAML file paths.
    tmp_dir : str
        The path of a temporary directory where colormap YAML files are stored when specifying a colormap
        on-the-fly with add_cmap_dict(cmap_dict).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            #  cls._instance = super(ColormapRegistry, cls).__new__(cls)
            cls._instance.registry = {}
            # Create temporary path
            cls._instance.tmp_dir = None
        return cls._instance

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls()  # this will call __new__
        return cls._instance

    def reset(self):
        """Clears the entire colormap registry."""
        self.registry.clear()

    @property
    def names(self):
        """List the names of all registered colormaps."""
        return sorted(list(self.registry))

    def __contains__(self, item):
        """Test registration of colormap in the registry."""
        return item in self.names

    def _check_if_cmap_in_use(self, name, force, verbose):
        if name in self.registry:
            if force and verbose:
                print(f"Warning: Overwriting existing colormap '{name}'")
            if not force:
                raise ValueError(f"A colormap named '{name}' already exists. To allow overwriting, set 'force=True'.")

    def register(self, filepath: str, verbose: bool = True, force: bool = True):
        """
        Register a colormap by its name and file path.

        Parameters
        ----------
        filepath : str
            The file path where the colormap's YAML file is located.
            The name of the colormap correspond to the name of the YAML file !
        verbose : bool, optional
            If True, the method will print a warning when overwriting an existing colormap. The default is True.
        force : bool, optional
            If True, it allow to overwrites an existing colormap. The default is True.
            If False, it raise an error if attempting to overwrite an existing colormap.

        Notes
        -----
        If a colormap with the same name already exists, it will be overwritten, and a warning will be printed.
        The validity of the colormap's YAML file is not validated !
        """
        # Check file exists
        if not os.path.isfile(filepath):
            raise ValueError(f"The colormap configuration YAML file {filepath} does not exist.")
        # Define colormap name
        name = os.path.splitext(os.path.basename(filepath))[0]
        # Check if the name is already used
        self._check_if_cmap_in_use(name=name, force=force, verbose=verbose)
        # Register
        self.registry[name] = filepath

    def add_cmap_dict(self, cmap_dict: dict, name: str, verbose: bool = True, force=True):
        """
        Add a colormap to the registry by providing a colormap dictionary and the colormap name.
        A temporary file YAML configuration file is created in self.tmp_dir.

        Parameters
        ----------
        cmap_dict : dict
            The colormap dictionary containing the colormap's configuration.
        name : str
            The name of the colormap.
        verbose : bool, optional
            If True, the method will print a warning when overwriting an existing colormap. The default is True.
        force : bool, optional
            If True, it allow to overwrites an existing colormap. The default is True.
            If False, it raise an error if attempting to overwrite an existing colormap.

        Notes
        -----
        If a colormap with the same name already exists, it will be overwritten, and a warning will be printed.
        The YAML file for the colormap is stored in a temporary directory.
        """
        # Create a temporary directory if not yet initiated
        if self.tmp_dir is None:
            self.tmp_dir = tempfile.mkdtemp(prefix="pycolorbar_cmaps_")
        # Check if the name is already used
        self._check_if_cmap_in_use(name=name, force=force, verbose=verbose)
        # Define filepath
        filename = f"{name}.yaml"
        filepath = os.path.join(self.tmp_dir, filename)
        # Write cmap_dict (and validate)
        write_cmap_dict(cmap_dict, filepath=filepath, force=True)
        # Update registry
        self.registry[name] = filepath

    def unregister(self, name: str):
        """
        Remove a colormap from the registry.

        Parameters
        ----------
        name : str
            The name of the colormap to remove.

        Raises
        ------
        ValueError
            If the colormap with the specified name is not registered.
        """
        if name in self.registry:
            _ = self.registry.pop(name)
        else:
            raise ValueError(f"The colormap {name} is not registered in pycolorbar.")

    def get_cmap_filepath(self, name: str):
        """
        Retrieve the colormap's YAML configuration file path.

        Parameters
        ----------
        name : str
            The name of the colormap.

        Returns
        -------
        str
            The colormap's YAML configuration file path.

        Raises
        ------
        ValueError
            If the colormap with the specified name is not registered.
        """
        # Remove _r suffix
        if name.endswith("_r"):
            name = name[:-2]
        # Retrieve filepath
        if name not in self.registry:
            raise ValueError(f"The {name} colormap is not registered in pycolorbar.")
        return self.registry[name]

    def get_cmap_dict(self, name: str):
        """
        Retrieve the validated colormap dictionary of a registered colormap.

        Parameters
        ----------
        name : str
            The name of the colormap.

        Returns
        -------
        dict
            The validated colormap dictionary.

        Raises
        ------
        ValueError
            If the colormap configuration is invalid or cannot be read.
        """
        filepath = self.get_cmap_filepath(name)
        return read_cmap_dict(filepath)

    def get_cmap(self, name: str):
        """
        Retrieve the colormap.

        Parameters
        ----------
        name : str
            The name of the colormap.

        Returns
        -------
        matplotlib.Colormap
            The matplotlib colormap.

        Raises
        ------
        ValueError
            If the colormap configuration is invalid or cannot be read.
        """
        from pycolorbar.settings.colormap_utility import create_cmap

        cmap_dict = self.get_cmap_dict(name)
        cmap = create_cmap(name=name, cmap_dict=cmap_dict)
        if name.endswith("_r"):
            cmap = cmap.reversed(name)
        return cmap

    def validate(self, name: str = None):
        """
        Validate the registered colormaps. If a specific name is provided, only that colormap is validated.

        Parameters
        ----------
        name : str, optional
            The name of a specific colormap to validate. If None, all registered colormaps are validated.

        Raises
        ------
        ValueError
            If any of the validated colormaps have invalid configurations.

        Notes
        -----
        Invalid colormap configurations are reported.
        """
        if isinstance(name, str):
            if name not in self.names:
                raise ValueError(f"{name} is not a registered colormap.")
            names = [name]

        else:
            names = self.names

        # Validate colormaps
        wrong_names = []
        for name in names:
            try:
                _ = self.get_cmap_dict(name)
            except Exception as e:
                wrong_names.append(name)
                print(f"{name} has an invalid configuration: {e}")
                print("")
        if wrong_names:
            raise ValueError(f"The {wrong_names} colormaps have invalid configurations.")
        return

    def to_yaml(self, name, filepath, force=False):
        """Write the colormap configuration to a YAML file."""
        cmap_dict = self.get_cmap_dict(name)
        write_cmap_dict(cmap_dict=cmap_dict, filepath=filepath, force=force)

    def _get_subset_names(self, category):
        names = []
        for name in self.names:
            cmap_dict = self.get_cmap_dict(name)
            categories = get_auxiliary_categories(cmap_dict)
            categories = [cat.upper() for cat in categories]
            if category.upper() in categories:
                names.append(name)
        return names

    def available(self, category=None, include_reversed=False):
        """List the name of available colormaps for a specific category."""
        if category is None:
            names = self.names
        else:
            names = self._get_subset_names(category=category)

        if include_reversed:
            names = [name + "_r" for name in names] + names
        return sorted(names)

    def show_colormap(self, name):
        """Display a colormap."""
        from pycolorbar.settings.colormap_visualization import plot_colormap

        cmap = self.get_cmap(name)
        plot_colormap(cmap)

    def show_colormaps(self, category=None, include_reversed=False, subplot_size=None):
        """Display available colormaps (optionally of a specific category)"""
        from pycolorbar.settings.colormap_visualization import plot_colormaps

        # Retrieve available colormaps (of a given category)
        names = self.available(category=category, include_reversed=include_reversed)
        if len(names) == 0:
            raise ValueError("No colormaps are yet registered in the pycolorbar ColormapRegistry.")

        # If only 1 colormap registered, plot it with the other method
        if len(names) == 1:
            self.show_colormap(name=names[0])
            return None

        # Else, retrieve colormaps to display
        cmaps = [self.get_cmap(name) for name in sorted(names)]

        # Display colormaps
        plot_colormaps(cmaps, subplot_size=subplot_size)


def register_colormaps(directory: str, name: str = None, verbose: bool = True, force: bool = True):
    """
    Register all colormap YAML files present in the specified directory (if name=None).

    This function assumes that all YAML files present in the directory are
    valid pycolorbar colormaps configuration files.

    Parameters
    ----------
    directory : str
        The directory where colormap YAML files are located.
    name : str, optional
        The specific name of a colormap to register. If None, all colormaps in the directory are registered.
    force : bool, optional
        If True, it allow to overwrites existing colormaps. The default is True.
        If False, it raise an error if attempting to overwrite an existing colormap.
    verbose : bool, optional
        If True, the method will print a warning when overwriting existing colormaps. The default is True.
    """
    colormaps = ColormapRegistry.get_instance()

    # List the colormap YAML files to register
    if name is not None:
        filepaths = [os.path.join(directory, f"{name}.yaml")]
    else:
        # List all YAML files in the directory
        filepaths = list_yaml_files(directory)

    # Add colormaps to the ColormapRegistry
    for filepath in filepaths:
        colormaps.register(filepath, verbose=verbose, force=force)


def register_colormap(filepath: str, verbose: bool = True, force: bool = True):
    """
    Register a single colormap YAML file.

    Parameters
    ----------
    filepath : str
        The file path where the colormap's YAML file is located.
        The name of the colormap correspond to the name of the YAML file !
    force : bool, optional
        If True, it allow to overwrites an existing colormap. The default is True.
        If False, it raise an error if attempting to overwrite an existing colormap.
    verbose : bool, optional
        If True, the method will print a warning when overwriting an existing colormap. The default is True.

    Raises
    ------
    ValueError
        If the specified colormap YAML file is not available in the directory or
        if trying to register an already registered colormap and `force=False`.
    """
    colormaps = ColormapRegistry.get_instance()
    colormaps.register(filepath, verbose=verbose, force=force)


def get_cmap_dict(name):
    """
    Retrieve the validated colormap dictionary of a registered colormap.

    Parameters
    ----------
    name : str
        The name of the colormap.

    Returns
    -------
    dict
        The validated colormap dictionary.

    Raises
    ------
    Exception
        If the colormap configuration is invalid or cannot be read.
    """
    colormaps = ColormapRegistry.get_instance()
    return colormaps.get_cmap_dict(name)


def get_cmap(name: str = None, lut: int = None):
    """
    Get a colormap instance.

    Parameters
    ----------
    name : str
        The name of a colormap known to pycolorbar or Matplotlib.
        If the name ends with the suffix `_r`, the colormap is reversed.
    lut : int or None
        If not `None` (the default), the colormap will be resampled to have *lut* entries in the lookup table.
        If the name ends with the suffix `_r`, the resampling is done after reversing the colormap.

    Returns
    -------
    Colormap
    """
    colormaps = ColormapRegistry.get_instance()

    # Use default matplotlib colormap
    if name is None:
        return plt.get_cmap(name=name, lut=lut)

    # If already colormap provided, return it
    if isinstance(name, mpl.colors.Colormap):
        return name

    # Retrieve registered colormaps names
    pycolorbar_registered_names = colormaps.names + [s + "_r" for s in colormaps.names]
    mpl_registered_names = plt.colormaps()

    # Check if reversed colormap
    has_r_suffix = name.endswith("_r")
    # Pycolorbar colormap
    if name in pycolorbar_registered_names:
        cmap = colormaps.get_cmap(name)
        if has_r_suffix:
            cmap = cmap.reversed()
        if lut is not None:
            cmap = cmap.resampled(lut)
        return cmap

    # Matplotlib registered colormap
    if name in mpl_registered_names:
        return plt.get_cmap(name=name, lut=lut)
    # Unavailable colormap
    else:
        raise ValueError(
            f"{name} is not registered in pycolorbar and matplotlib !\n "
            f"Valid matplotlib colormap are {mpl_registered_names}.\n "
            f"Valid pycolorbar colormap are {pycolorbar_registered_names}."
        )


def _get_mpl_cmap_by_category(category):
    """Return matplotlib colormap names by category.

    See: https://matplotlib.org/stable/users/explain/colors/colormaps.html#choosing-colormaps
    """
    type_dict = {
        "PERCEPTUAL": ["viridis", "plasma", "inferno", "magma", "cividis"],  # PERCEPTUALLY UNIFORM
        "SEQUENTIAL": [
            "viridis",
            "plasma",
            "inferno",
            "magma",
            "cividis",
            "Greys",
            "Purples",
            "Blues",
            "Greens",
            "Oranges",
            "Reds",
            "YlOrBr",
            "YlOrRd",
            "OrRd",
            "PuRd",
            "RdPu",
            "BuPu",
            "GnBu",
            "PuBu",
            "YlGnBu",
            "PuBuGn",
            "BuGn",
            "YlGn",
            "binary",
            "gist_yarg",
            "gist_gray",
            "gray",
            "bone",
            "pink",
            "spring",
            "summer",
            "autumn",
            "winter",
            "cool",
            "Wistia",
            "hot",
            "afmhot",
            "gist_heat",
            "copper",
        ],
        "DIVERGING": [
            "PiYG",
            "PRGn",
            "BrBG",
            "PuOr",
            "RdGy",
            "RdBu",
            "RdYlBu",
            "RdYlGn",
            "Spectral",
            "coolwarm",
            "bwr",
            "seismic",
        ],
        "QUALITATIVE": [
            "Pastel1",
            "Pastel2",
            "Paired",
            "Accent",
            "Dark2",
            "Set1",
            "Set2",
            "Set3",
            "tab10",
            "tab20",
            "tab20b",
            "tab20c",
        ],
        "CYCLIC": ["twilight", "twilight_shifted", "hsv"],
    }
    type_dict["CATEGORICAL"] = type_dict["QUALITATIVE"]
    if category.upper() in type_dict:
        names = type_dict[category.upper()]
    else:
        names = []
    return names


def _get_matplotlib_cmaps(category=None, include_reversed=False):
    if category is None:
        names = plt.colormaps()
        names = [name for name in names if not name.endswith("_r")]
    else:
        names = _get_mpl_cmap_by_category(category=category)
    # Include names with _r suffix
    if include_reversed:
        names = [name + "_r" for name in names] + names
    return names


def available_colormaps(category=None, include_reversed=False):
    colormaps = ColormapRegistry.get_instance()
    names = colormaps.available(category=category, include_reversed=include_reversed)
    names += _get_matplotlib_cmaps(category=category, include_reversed=include_reversed)
    names = sorted(np.unique(names))
    return names
