import numpy as np
from sklearn.mixture import gaussian_mixture  as gauss
from sklearn.metrics.pairwise import cosine_similarity
import cv2
import os
import functions as fun
import time


'''This script is the main script of the make and model recognition using unsupervised learning
All of the functions used are in functions.py file
'''
#Number of SIFT components that we will be keeping after PCA reduction, original number of components is 128
pc_comp=100

#Booleans that keep track of the fisher vector pipeline
compute_all_steps=True

#paths that will be used for our proof of concept
#in further stage of the implementation we will have only one folder that we will be working with
paths=["aston","bmw","clio","dodge","peugot"]

#First we define the PCA REDUCTOR MATRICE
#This is the matrice that will be used to keep a certain amount of SIFT components
#Name of the file that stores the reducer matrice that will be used for the PCA reduction process
id="reducer"

covariance_type="diag"

#Check to see if there is a reducer file, if not create one 
if(not(os.path.isfile(id+".npy")) or compute_all_steps):
	print("No reducer file was found")
	print("A new reducer file is being generated...")
	fun.compute_save_reduce_vector(paths,id,pc_comp=pc_comp)
	print("The Reducer file has been generated")
	print("\n")

#Once the reducer file has been created it is time to load it and use it for PCA Reduction 
print("Loading reducer file...")
reducer=np.load(id+".npy")
print("Reducer file loaded")
print("\n")


#Creation and storage of Reduced ROOT SIFT VECTORS
if(compute_all_steps):
	print("No root sift files were found")
	print("Generating root sift files...")
	fun.compute_save_reduced_root_sift(reducer,paths)
	print("Reduced root sift files generated and saved")
	print("\n")
	
#Load all of the saved ROOT SIFT DESCRIPTORS and then use them to fit a GMM model
"""Implementation that has to be kept """
descriptors=np.atleast_2d(np.asarray(fun.file_counter(paths,".npy","reduced_data",remove=False,loader=True)))
print("the shape of the descriptors using the second function is ", descriptors.shape)

#Check to see if there are any trained GMM models
#If so load them and use them to create a fisher vector 
#We will be using a range 
for gmm_comp in range(50,1000,50):
	gmm_means_file="./GMM/means"+str(gmm_comp)+".gmm.npy"
	gmm_covariance_file="./GMM/covs"+str(gmm_comp)+".gmm.npy"
	gmm_weight_file="./GMM/weights"+str(gmm_comp)+".gmm.npy"
	if(os.path.isfile(gmm_means_file) and os.path.isfile(gmm_covariance_file) and os.path.isfile(gmm_weight_file)):
		print("all the GMM files are in place and now we are going to load them")
		print("loading files...")
		gmm_means_file="./GMM/means"+str(gmm_comp)+".gmm.npy"
		gmm_covariance_file="./GMM/covs"+str(gmm_comp)+".gmm.npy"
		gmm_weight_file="./GMM/weights"+str(gmm_comp)+".gmm.npy"
		means=np.load(gmm_means_file)
		covs=np.load(gmm_covariance_file)
		weights=np.load(gmm_weight_file)
		print("GMM "+str(gmm_comp)+" loaded")
		print("\n")
	else: 
		# print("we did not find all of our files")
		# print("we train a GMM Model")
		# print("gathering ROOT SIFT descriptors...")
		# descriptors=fun.compute_save_reduce_vector(paths,id,pc_comp=pc_comp,reduced=True).T
		descriptors=np.atleast_2d(np.asarray(fun.file_counter(paths,".npy","reduced_data",remove=False,loader=True)))
		# print("descriptors gathered")
		print("training GMM %d..."%(gmm_comp))
		
		#GMM MODEL
		GMM=gauss.GaussianMixture(n_components=gmm_comp,covariance_type=covariance_type,max_iter=100000,n_init=1,init_params="kmeans")
		GMM.fit(descriptors)
		# print(np.sum(GMM.predict_proba(descriptors[0:20]),axis=1))
		print("trained GMM %d..."%(gmm_comp))
		print("saving the GMM model")
		means=GMM.means_
		covs=GMM.covariances_
		weights=GMM.weights_
		
		gmm_means_file="./GMM/means"+str(gmm_comp)+".gmm.npy"
		gmm_covariance_file="./GMM/covs"+str(gmm_comp)+".gmm.npy"
		gmm_weight_file="./GMM/weights"+str(gmm_comp)+".gmm.npy"
		
		np.save(gmm_means_file,means)
		np.save(gmm_covariance_file,covs)
		np.save(gmm_weight_file,weights)
		# print("GMM model has been saved")
		print("\n")

	# now we check to see if there is any fisher vector
	num_fis=fun.file_counter(paths,".npy","fisher_vectors",remove=False)
	if(compute_all_steps):
		# print("No fisher vector files were found")
		# print("generating them...")
		print("Generate and Save fisher files for GMM %d..."%(gmm_comp))
		fun.generate_fisher_vectors(paths,means,covs,weights,"_"+str(gmm_comp))
		print("Fisher files saved")
		print("\n")
		# print("loading our fisher files...")
		# fisher_vectors=np.atleast_2d(fun.file_counter(paths,".npy","fisher_vectors",remove=False,loader=True))
		# print("fisher files have been generated")
		# print(fisher_vectors.shape)
	else:
		print("we found our fisher files")
		print("loading our fisher files...")
		# fisher_vectors=np.atleast_2d(fun.file_counter(paths,".npy","fisher_vectors",remove=False,loader=True))
		# print(fisher_vectors.shape)'''
		
######################################
# FINAL STAGE OF PROOF OF CONCEPT    #
######################################


evaluation="data.txt"
for case in paths :
	max_value=0
	max_comp=0
	min_value=1000
	best_gmms=5

	data=[]
	for gmm_comp in range(50,1000,50):
		target=open(evaluation,"a")
		evaluation_limit=10
		print("-------------------------------------------------")
		print("evaluation of GMM %d for %s"%(gmm_comp,case))
		# paths=["aston","bmw","clio","dodge","peugot"]
		fisher_vectors=np.atleast_2d(fun.file_counter(paths,"_"+str(gmm_comp)+".npy","fisher_vectors",remove=False,loader=True,Fisher=True))
		cosine_metric=cosine_similarity(fisher_vectors)
		all_bmw=0		
		all_clio=0			
		all_dodge=0			
		all_peugot=0				
		all_aston=0	


		if(case=="aston"):
			under=5
			upper=15
		if(case=="bmw"):
			under=25
			upper=35
		if(case=="clio"):
			under=45
			upper=55
		if(case=="dodge"):
			under=65
			upper=75
		if(case=="peugot"):
			under=85
			upper=95
		
		for ind in range(under,upper):
			if(ind<20):
				current=all_aston
				case="aston"
			if(ind>19 and ind<40):
				current=all_bmw
				case="bmw"
			if(ind>39 and ind<60):
				current=all_clio
				case="clio"
			if(ind>59 and ind<80):
				current=all_dodge
				case="dodge"
			if(ind>79 and ind<100):
				current=all_peugot
				case="peugot"
			indices=np.flip(np.argsort(cosine_metric[ind]),axis=0)
			aston=0
			bmw=0
			dodge=0
			clio=0
			peugot=0
			clio_translate=0
			for  sim in range(1,(evaluation_limit+1)):
			
				if(indices[sim]<20):
					aston=aston+1
				if(indices[sim]>19 and indices[sim]<40):
					bmw=bmw+1
				if(indices[sim]>39 and indices[sim]<60):
					clio=clio+1
				if(indices[sim]>59 and indices[sim]<80):
					dodge=dodge+1
				if(indices[sim]>79 and indices[sim]<100):
					peugot=peugot+1
			# print("there are %d ASTON vehicles in the first %d images"%(aston,evaluation_limit))		
			# print("there are %d BMW vehicles in the first %d images"%(bmw,evaluation_limit))		
			# print("there are %d CLIO vehicles in the first %d images"%(clio,evaluation_limit))		
			# print("there are %d DODGE vehicles in the first %d images"%(dodge,evaluation_limit))		
			# print("there are %d PEUGOT vehicles in the first %d images"%(peugot,evaluation_limit))		
			# print("\n")
			"""for sim in range(5):
			
				if(indices[sim]<20):
					# print("./buildings/%03d.png"%(indices[sim]+1))
					if (indices[sim]==0):
						image=cv2.imread("./aston/%03d.png"%(indices[sim]+1))
					else:
						image=cv2.imread("./aston/%03d.png"%(indices[sim]))
					height, width = image.shape[:2]
					image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
					if(sim==0):
						cv2.imshow("original",image)
					else:
						cv2.imshow("similar %d"%(sim),image)
						
						
				if(indices[sim]>19 and indices[sim]<40):
					# print("./buildings/%03d.png"%(indices[sim]+1))
					image=cv2.imread("./bmw/%03d.png"%(indices[sim]+1-20))
					height, width = image.shape[:2]
					image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
					if(sim==0):
						cv2.imshow("original",image)
					else:
						cv2.imshow("similar %d"%(sim),image)
						
						
				if(indices[sim]>39 and indices[sim]<60):
					# print("./buildings/%03d.png"%(indices[sim]+1))
					image=cv2.imread("./clio/%03d.png"%(indices[sim]+1-40))
					height, width = image.shape[:2]
					image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
					if(sim==0):
						cv2.imshow("original",image)
					else:
						cv2.imshow("similar %d"%(sim),image)
						
						
						
				if(indices[sim]>59 and indices[sim]<80):
					# print("./buildings/%03d.png"%(indices[sim]+1))
					image=cv2.imread("./dodge/%03d.png"%(indices[sim]+1-60))
					height, width = image.shape[:2]
					image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
					if(sim==0):
						cv2.imshow("original",image)
					else:
						cv2.imshow("similar %d"%(sim),image)
						
						
				if(indices[sim]>79 and indices[sim]<90):
					image=cv2.imread("./peugot/%03d.png"%(indices[sim]+1-80))
					height, width = image.shape[:2]
					image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
					if(sim==0):
						cv2.imshow("original",image)
					else:
						cv2.imshow("similar %d"%(sim),image)
				
				if(indices[sim]>99):
					image=cv2.imread("./cliotranslate/%03d.png"%(indices[sim]+1-100))
					height, width = image.shape[:2]
					image = cv2.resize(image,(2*width, 2*height), interpolation = cv2.INTER_CUBIC)
					if(sim==0):
						cv2.imshow("original",image)
					else:
						cv2.imshow("similar %d"%(sim),image)"""
								
			all_bmw+=bmw			
			all_clio+=clio			
			all_dodge+=dodge			
			all_peugot+=peugot			
			all_aston+=aston	
			# all_clio_translate+=clio_translate
			# cv2.imshow("image",np.zeros((100,1000,3)))
			# cv2.waitKey(0)
		# print("Overall GMM with %d components gives us : "%gmm_comp)
		# print("BMW: %d"%all_bmw)
		# print("CLIO: %d"%all_clio)
		# print("DODGE: %d"%all_dodge)
		# print("PEUGOT: %d"%all_peugot)
		# print("ASTON: %d"%all_aston)
		# print("Number of vehicles : %d"%(all_bmw+all_clio+all_dodge+all_peugot+all_aston))
		max_comp,max_value=(gmm_comp,current) if max_value<current else (max_comp,max_value)
		min_comp,min_value=(gmm_comp,current) if min_value>current else (min_comp,min_value)
		data.append((current,gmm_comp))
		# print("\n")
		data.sort(key=lambda tup: tup[0])
		data.reverse()
		# print("best comp is %d yielding " %(max_comp))
		# cv2.imshow("image",np.zeros((100,1000,3)))
		# cv2.waitKey(0)
		print("-------------------------------------------------")
	mean_recall=0
	mean_gmm=0
	for i in range(best_gmms):
		mean_recall+=data[i][0]
		mean_gmm+=data[i][1]
	mean_recall=mean_recall/best_gmms
	mean_gmm=mean_gmm/best_gmms
	
	target.write("Evaluation of model %s yields "%(case))
	target.write("\n")
	target.write("[")
	for d in data:
		target.write("("+str(d[0])+","+str(d[1])+")")
	target.write("]")
	target.write("\n")
	target.write("best mean GMM is %s and best mean recall is %s"%(str(mean_gmm),str(mean_recall)))
	target.write("\n"*2)
	
	print("best comp is %d yielding %d " %(max_comp,max_value))
	print("worst comp is %d yielding %d " %(min_comp,min_value))
	print(data)
	# break'''
target.close()





























