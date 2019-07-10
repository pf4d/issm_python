dirs="dump/results/dx_2000/unstructured/*"
regex="([a-z0-9\_\/]+_beta_)([0-9]+)*"
for i in $dirs; do
	if [[ $i =~ $regex ]]
	then
		name="${BASH_REMATCH[1]}${BASH_REMATCH[2]}_dx_2000"
		echo "EXE: mv $i ${name}"
		mv $i ${name}
	else
		echo "$i doesn't match" >&2
	fi
done
