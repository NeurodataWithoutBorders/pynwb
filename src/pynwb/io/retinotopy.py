# from hdmf.build import ObjectMapper
# from .. import register_map
# from pynwb.retinotopy import ImagingRetinotopy
#
#
# @register_map(ImagingRetinotopy)
# class ImagingRetinotopyMap(ObjectMapper):
#
#     def __init__(self, spec):
#         super().__init__(spec)
#
#         datasets = ['sign_map', 'axis_1_phase_map']
#         for dataset_name in datasets:
#             self.map_spec(dataset_name, spec.get_dataset(dataset_name))
