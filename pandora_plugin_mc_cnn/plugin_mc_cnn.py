#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright: (c) 2019 Centre National d'Etudes Spatiales

"""
This module contains all functions to calculate the cost volume with mc-cnn networks
"""

from typing import Dict, Union
import os
from json_checker import Checker, And
import xarray as xr

from pandora.stereo import stereo
from mc_cnn.run import run_mc_cnn_fast, run_mc_cnn_accurate


@stereo.AbstractStereo.register_subclass('mc_cnn')
class MCCNN(stereo.AbstractStereo):
    """

    MCCNN class is a plugin that create a cost volume by calling the McCNN library: a neural network that produce a
    similarity score

    """
    # Type of mc_cnn architecture : fast or accurate
    _MC_CNN_ARCH = None
    _WINDOW_SIZE = 11
    _SUBPIX = 1
    # Path to the pretrained model
    _MODEL_PATH = None

    def __init__(self, **cfg: Union[int, str]):
        """

        :param cfg: optional configuration, {'stereo_method': value, 'mc_cnn_arch': 'fast' | 'accurate',
        'window_size': value, 'subpix': value, 'model_path' :value}
        :type cfg: dictionary
        """
        self.cfg = self.check_config(**cfg)
        self._mc_cnn_arch = str(self.cfg['mc_cnn_arch'])
        self._model_path = str(self.cfg['model_path'])
        self._window_size = self.cfg['window_size']
        self._subpix = self.cfg['subpix']

    def check_config(self, **cfg: Union[int, str]) -> Dict[str, Union[int, str]]:
        """
        Add default values to the dictionary if there are missing elements and check if the dictionary is correct

        :param cfg: stereo configuration
        :type cfg: dict
        :return cfg: stereo configuration updated
        :rtype: dict
        """
        # Give the default value if the required element is not in the configuration
        if 'window_size' not in cfg:
            cfg['window_size'] = self._WINDOW_SIZE
        if 'subpix' not in cfg:
            cfg['subpix'] = self._SUBPIX

        schema = {
            'stereo_method': And(str, lambda x: x == 'mc_cnn'),
            'window_size': And(int, lambda x: x == 11),
            'subpix': And(int, lambda x: x == 1),
            'mc_cnn_arch': And(str, lambda x: x in ('fast', 'accurate')),
            'model_path': And(str, lambda x: os.path.exists(x))
        }

        checker = Checker(schema)
        checker.validate(cfg)
        return cfg

    def desc(self):
        """
        Describes the optimization method

        """
        print('MC-CNN similarity measure')

    def compute_cost_volume(self, img_left: xr.Dataset, img_right: xr.Dataset, disp_min: int, disp_max: int
                            ) -> xr.Dataset:
        """
        Computes the cost volume for a pair of images

        :param img_left: left Dataset image
        :type img_left:
            xarray.Dataset containing :
                - im : 2D (row, col) xarray.DataArray
                - msk : 2D (row, col) xarray.DataArray
        :param img_right: right Dataset image
        :type img_right:
            xarray.Dataset containing :
                - im : 2D (row, col) xarray.DataArray
                - msk : 2D (row, col) xarray.DataArray
        :param disp_min: minimum disparity
        :type disp_min: int
        :param disp_max: maximum disparity
        :type disp_max: int
        :return: the cost volume dataset
        :rtype:
            xarray.Dataset, with the data variables:
                - cost_volume 3D xarray.DataArray (row, col, disp)
                - confidence_measure 3D xarray.DataArray (row, col, indicator)
        """
        if self._mc_cnn_arch == 'fast':
            cv = run_mc_cnn_fast(img_left, img_right, disp_min, disp_max, self._model_path)

        # Accurate architecture
        else:
            cv = run_mc_cnn_accurate(img_left, img_right, disp_min, disp_max, self._model_path)

        # Allocate the xarray cost volume
        metadata = {'measure': 'mc_cnn_' + self._mc_cnn_arch, 'subpixel': self._subpix,
                    'offset_row_col': int((self._window_size - 1) / 2), 'window_size': self._window_size,
                    'type_measure': 'min', 'cmax': 1}
        cv = self.allocate_costvolume(img_left, self._subpix, disp_min, disp_max, self._window_size, metadata, cv)

        return cv
