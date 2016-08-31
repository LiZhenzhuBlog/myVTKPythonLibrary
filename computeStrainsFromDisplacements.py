#coding=utf8

########################################################################
###                                                                  ###
### Created by Martin Genet, 2012-2016                               ###
###                                                                  ###
### University of California at San Francisco (UCSF), USA            ###
### Swiss Federal Institute of Technology (ETH), Zurich, Switzerland ###
### École Polytechnique, Palaiseau, France                           ###
###                                                                  ###
########################################################################

import numpy
import vtk

import myVTKPythonLibrary as myVTK
from mat_vec_tools import *

########################################################################

def computeStrainsFromDisplacements(
        mesh,
        disp_array_name="displacement",
        mesh_w_local_basis=None,
        verbose=0):

    myVTK.myPrint(verbose, "*** computeStrainsFromDisplacements ***")

    myVTK.computeDeformationGradientsFromDisplacements(
        mesh=mesh,
        disp_array_name=disp_array_name,
        verbose=verbose-1)
    assert (mesh.GetCellData().HasArray("DeformationGradient"))
    farray_f = mesh.GetCellData().GetArray("DeformationGradient")

    n_cells = mesh.GetNumberOfCells()
    if (mesh_w_local_basis is not None):
        farray_strain = myVTK.createFloatArray(
            name="Strain_CAR",
            n_components=6,
            n_tuples=n_cells)
    else:
        farray_strain = myVTK.createFloatArray(
            name="Strain",
            n_components=6,
            n_tuples=n_cells)
    mesh.GetCellData().AddArray(farray_strain)
    I = numpy.eye(3)
    E_vec = numpy.empty(6)
    #e_vec = numpy.empty(6)
    for k_cell in range(n_cells):
        F = numpy.reshape(farray_f.GetTuple(k_cell), (3,3), order="C")
        C = numpy.dot(numpy.transpose(F), F)
        E = (C - I)/2
        mat_sym33_to_vec_col6(E, E_vec)
        farray_strain.SetTuple(k_cell, E_vec)
        #if (add_almansi_strain):
            #Finv = numpy.linalg.inv(F)
            #c = numpy.dot(numpy.transpose(Finv), Finv)
            #e = (I - c)/2
            #mat_sym33_to_vec_col6(e, e_vec)
            #farray_almansi.SetTuple(k_cell, e_vec)

    if (mesh_w_local_basis is not None):
        if (mesh_w_local_basis.GetCellData().HasArray("eR")) and (mesh_w_local_basis.GetCellData().HasArray("eC")) and (mesh_w_local_basis.GetCellData().HasArray("eL")):
            farray_strain_cyl = myVTK.rotateMatrix(
                old_array=mesh.GetCellData().GetArray("Strain_CAR"),
                out_vecs=[mesh_w_local_basis.GetCellData().GetArray("eR"),
                          mesh_w_local_basis.GetCellData().GetArray("eC"),
                          mesh_w_local_basis.GetCellData().GetArray("eL")],
                verbose=0)
            farray_strain_cyl.SetName("Strain_CYL")
            mesh.GetCellData().AddArray(farray_strain_cyl)

        if (mesh_w_local_basis.GetCellData().HasArray("eRR")) and (mesh_w_local_basis.GetCellData().HasArray("eCC")) and (mesh_w_local_basis.GetCellData().HasArray("eLL")):
            farray_strain_pps = myVTK.rotateMatrix(
                old_array=mesh.GetCellData().GetArray("Strain_CAR"),
                out_vecs=[mesh_w_local_basis.GetCellData().GetArray("eRR"),
                          mesh_w_local_basis.GetCellData().GetArray("eCC"),
                          mesh_w_local_basis.GetCellData().GetArray("eLL")],
                verbose=0)
            farray_strain_pps.SetName("Strain_PPS")
            mesh.GetCellData().AddArray(farray_strain_pps)
